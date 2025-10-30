#!/bin/bash
set -e
# --- Ensure script is run from the project root (where main.nf and nextflow.config exist) ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ ! -f "$SCRIPT_DIR/main.nf" ] || [ ! -f "$SCRIPT_DIR/nextflow.config" ]; then
    echo -e "\033[1;31mError:\033[0m Please run this script from inside the cloned Genomic Dashboard directory."
    echo "Example:"
    echo "    cd genomic-dashboard"
    echo "    bash genomic_dashboard.sh"
    exit 1
fi

APP_NAME="Genomic Dashboard"
IMAGE_NAME="genomic_dashboard_v1.0"
INSTALL_DIR="$HOME/software/genomic-dashboard"
DB_DIR="$INSTALL_DIR/database"
LAUNCHER="/usr/local/bin/genomic-dashboard"
CONFIG_FILE="$INSTALL_DIR/nextflow.config"

# --- URLs for required databases ---
URL_BGC="https://zenodo.org/records/15659134/files/BGC_cyanotoxins_plus_orthologs.fna"
URL_CYANO="https://zenodo.org/records/15659134/files/cyanobacteriota_ncbi_dRep_n220.tar.gz"
URL_KRAKEN="https://genome-idx.s3.amazonaws.com/kraken/k2_viral_20250714.tar.gz"

# --- Pretty print helpers ---
log()   { echo -e "\033[1;32m$1\033[0m"; }
warn()  { echo -e "\033[1;33m$1\033[0m"; }
error() { echo -e "\033[1;31m$1\033[0m"; }

# =====================================================================
# INSTALLATION SECTION
# =====================================================================
install_app() {
    echo ""
    log "Installing $APP_NAME..."
    echo ""

    # --- Check dependencies ---
    for dep in docker curl tar sed; do
        if ! command -v $dep &>/dev/null; then
            error "$dep not found. Please install it first."
            exit 1
        fi
    done

    # --- Copy project to install directory ---
    log "Copying project files to $INSTALL_DIR ..."
    mkdir -p "$INSTALL_DIR"
    # Copy only from the validated project root
    cd "$SCRIPT_DIR"
    rsync -a --exclude '.git' --exclude '.*' "$SCRIPT_DIR/" "$INSTALL_DIR/"

    # --- Ensure database directory exists ---
    mkdir -p "$DB_DIR"

    # -----------------------------------------------------------------
    # Helper: download + extract if needed
    # -----------------------------------------------------------------
    handle_db() {
        local url="$1"
        local dest="$2"
        local unpack_dir="$3"
        local filename=$(basename "$dest")

        # Already extracted → nothing to do
        if [ -d "$unpack_dir" ]; then
            log "Found extracted: $(basename "$unpack_dir")"
            return
        fi

        # Archive exists but not extracted → extract
        if [ -f "$dest" ]; then
            log "Extracting $filename ..."
            mkdir -p "$DB_DIR"/${filename%.tar.gz} && tar -xzf "$dest" -C "$DB_DIR"/${filename%.tar.gz}
            return
        fi

        # Missing → download + extract
        warn "Missing: $filename — downloading..."
        if ! curl -L -o "$dest" "$url"; then
            error "Failed to download $filename"
            exit 1
        fi
        log "Downloaded $filename"
        if [[ "$filename" == *.tar.gz ]]; then
            log "Extracting $filename ..."
            mkdir -p "$DB_DIR"/${filename%.tar.gz} && tar -xzf "$dest" -C "$DB_DIR"/${filename%.tar.gz}
        fi
    }

    # -----------------------------------------------------------------
    # Handle each database
    # -----------------------------------------------------------------
    # 1. BGC (fasta, no extraction)
    if [ ! -f "$DB_DIR/BGC_cyanotoxins_plus_orthologs.fna" ]; then
        warn "Downloading BGC database..."
        curl -L -o "$DB_DIR/BGC_cyanotoxins_plus_orthologs.fna" "$URL_BGC"
        log "Downloaded BGC_cyanotoxins_plus_orthologs.fna"
    else
        log "BGC database already present."
    fi

    # 2. Cyanobacteria (tar.gz)
    handle_db "$URL_CYANO" \
        "$DB_DIR/cyanobacteriota_ncbi_dRep_n220.tar.gz" \
        "$DB_DIR/cyanobacteriota_ncbi_dRep_n220"

    # 3. Kraken (tar.gz)
    handle_db "$URL_KRAKEN" \
        "$DB_DIR/k2_viral_20250714.tar.gz" \
        "$DB_DIR/k2_viral_20250714"

    # -----------------------------------------------------------------
    # Update nextflow.config
    # -----------------------------------------------------------------
    log "Updating nextflow.config paths..."
    if [ ! -f "$CONFIG_FILE" ]; then
        warn "nextflow.config not found — creating default one."
        cat > "$CONFIG_FILE" <<EOF
nextflow.enable.dsl=2

manifest {
  name = 'RosHAB'
  description = 'Taxonomic identification of ONT reads'
  mainScript = 'main.nf'
}

process.cpus = '8'

params {
  help = false
  skip_qc = false
  kraken_db = ''
  coverm_ncbi_db = ''
  minimap_gene_db = ''
}
EOF
    fi

    REL_BGC="/database/BGC_cyanotoxins_plus_orthologs.fna"
    REL_CYANO="/database/cyanobacteriota_ncbi_dRep_n220/cyanobacteriota_ncbi_dRep_n220"
    REL_KRAKEN="/database/k2_viral_20250714"
    CONFIG_FILE="$HOME/software/genomic-dashboard/nextflow.config"

    if sed --version >/dev/null 2>&1; then
        SED_CMD="sed -i"
    else
        SED_CMD="sed -i ''"
    fi

    $SED_CMD "s|kraken_db *=.*|kraken_db = '${REL_KRAKEN}'|" "$CONFIG_FILE"
    $SED_CMD "s|coverm_ncbi_db *=.*|coverm_ncbi_db = '${REL_CYANO}'|" "$CONFIG_FILE"
    $SED_CMD "s|minimap_gene_db *=.*|minimap_gene_db = '${REL_BGC}'|" "$CONFIG_FILE"

    log "nextflow.config updated."

    # -----------------------------------------------------------------
    # Build Docker image
    # -----------------------------------------------------------------
    if ! docker image inspect "$IMAGE_NAME" >/dev/null 2>&1; then
        log "Building Docker image: $IMAGE_NAME ..."
        if ! docker build -t "$IMAGE_NAME" "$INSTALL_DIR"; then
            error "Docker build failed."
            exit 1
        fi
    else
        log "Docker image $IMAGE_NAME already exists"
    fi

    # -----------------------------------------------------------------
    # Create launcher
    # -----------------------------------------------------------------
    log "Creating launcher..."
    sudo bash -c "cat > '$LAUNCHER' <<'EOF'
#!/bin/bash
$INSTALL_DIR/install.sh
EOF"
    chmod +x "$LAUNCHER"

    log "Installation complete"
    echo ""
    log "Run the dashboard anytime with: genomic-dashboard"
    echo ""
}

# =====================================================================
# LAUNCH SECTION
# =====================================================================
launch_app() {
    IMAGE_NAME="genomic_dashboard_v1.0"

    # ---- GUI folder selection ----
    select_directory_macos() {
        osascript <<EOT
            try
                set chosenFolder to choose folder with prompt "Select a folder containing FASTQ files"
                POSIX path of chosenFolder
            on error
                return ""
            end try
EOT
    }

    select_directory_linux() {
        if command -v zenity >/dev/null 2>&1; then
            zenity --file-selection --directory --title="Select a directory"
        elif command -v kdialog >/dev/null 2>&1; then
            kdialog --getexistingdirectory . "Select a directory"
        else
            echo ""
        fi
    }

    # ---- Detect OS ----
    OS=$(uname)
    case "$OS" in
        Darwin) CHOSEN_DIR=$(select_directory_macos) ;;
        Linux)  CHOSEN_DIR=$(select_directory_linux) ;;
        *)      error "Unsupported OS: $OS"; exit 1 ;;
    esac

    # ---- Validate ----
    if [[ -z "$CHOSEN_DIR" ]]; then
        echo "No directory selected. Exiting."
        exit 1
    fi

    CHOSEN_DIR="${CHOSEN_DIR%/}"
    echo "Selected directory: $CHOSEN_DIR"

    # ---- Ensure Docker image ----
    if ! docker image inspect "$IMAGE_NAME" >/dev/null 2>&1; then
        warn "Docker image not found. Running installation first..."
        install_app
    fi

    # ---- Stop running container if exists ----
    if docker ps --filter "name=${IMAGE_NAME}_container" --format '{{.Names}}' | grep -q "${IMAGE_NAME}_container"; then
        warn "Stopping existing container..."
        docker stop "${IMAGE_NAME}_container" >/dev/null 2>&1 || true
    fi

    # ---- Run container ----
    echo "Starting Docker container..."
    docker run -d --rm \
        -v "$CHOSEN_DIR":"$CHOSEN_DIR" \
        -v "$DB_DIR":/database \
        -e INPUT_DIR="$CHOSEN_DIR" \
        -p 8000:5000 \
        --name "${IMAGE_NAME}_container" \
        "$IMAGE_NAME"

    # ---- Wait for server ----
    echo "Waiting for server to start..."
    MAX_WAIT=30
    SLEEP_INTERVAL=2
    ELAPSED=0
    until curl -s http://localhost:8000 >/dev/null; do
        sleep $SLEEP_INTERVAL
        ELAPSED=$((ELAPSED + SLEEP_INTERVAL))
        if [ $ELAPSED -ge $MAX_WAIT ]; then
            echo "Server did not start within $MAX_WAIT seconds."
            docker stop "${IMAGE_NAME}_container" >/dev/null 2>&1
            exit 1
        fi
    done

    # ---- Open browser ----
    URL="http://localhost:8000"
    echo "Opening $URL..."
    if [[ "$OS" == "Darwin" ]]; then
        open "$URL"
    elif [[ "$OS" == "Linux" ]]; then
        if command -v xdg-open >/dev/null 2>&1; then
            xdg-open "$URL"
        elif command -v gnome-open >/dev/null 2>&1; then
            gnome-open "$URL"
        else
            echo "Please open $URL manually."
        fi
    fi
}

# =====================================================================
# MAIN ENTRYPOINT — auto-install if needed
# =====================================================================
if [ ! -d "$INSTALL_DIR" ] || [ ! "$(docker images -q $IMAGE_NAME 2>/dev/null)" ]; then
    install_app
fi

launch_app

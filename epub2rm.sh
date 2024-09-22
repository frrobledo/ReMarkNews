#!/bin/bash

# Default parameter settings
REMARKABLE=${HOME}/remarkable

# Function to process a single EPUB file
process_epub() {
    epub=$1
    if [ -f ${epub} ]; then
        name=$(basename ${epub} .epub)
        date="$(date +%s)000"
        echo "Processing EPUB document ${name}, date ${date}"
        temp=$(mktemp --directory rm.XXXXX)
        echo "Resulting documents in ${temp}"

        # Create unique identifier
        uuid=$(uuidgen)
        echo "Creating $uuid document directories."
        dest=${temp}/${uuid}
        mkdir ${dest}
        mkdir ${dest}.{cache,highlights,textconversion,thumbnails}
        cp ${epub} ${dest}.epub

        # Create content file
        cat > ${dest}.content <<EOF
{
    "extraMetadata": {},
    "fileType": "epub",
    "fontName": "",
    "lastOpenedPage": 0,
    "lineHeight": -1,
    "margins": 100,
    "orientation": "portrait",
    "pageCount": 0,
    "pages": [],
    "textScale": 1,
    "transform": {
        "m11": 1, "m12": 0, "m13": 0,
        "m21": 0, "m22": 1, "m23": 0,
        "m31": 0, "m32": 0, "m33": 1
    }
}
EOF

        # Create metadata file
        cat > ${dest}.metadata <<EOF
{
    "deleted": false,
    "lastModified": "${date}",
    "metadatamodified": false,
    "modified": false,
    "parent": "",
    "pinned": false,
    "synced": false,
    "type": "DocumentType",
    "version": 1,
    "visibleName": "${name}"
}
EOF

        # Create empty pagedata file
        touch ${dest}.pagedata

        # Generate thumbnail
        convert "${epub}[0]" -monochrome -scale 362x512 ${dest}.thumbnails/0.jpg

        # Copy files to the ReMarkable directory
        ( cd ${temp} ; tar cf - . | \
              (cd ${REMARKABLE}/home/root/.local/share/remarkable/xochitl/ ; tar xvf - ))

        # Clean up temporary directory
        rm -rf ${temp}

        echo "Processed ${name}"
    fi
}

# Main script execution
for epub in "$@"
do
    process_epub "$epub"
done

# Restart xochitl on the ReMarkable tablet
REMARKABLE_IP="192.168.1.164"  # Replace with your tablet's IP or hostname
REMARKABLE_PASSWORD="KnnGR6W0MX"  # Replace with your tablet's password
sshpass -p $REMARKABLE_PASSWORD ssh root@$REMARKABLE_IP systemctl restart xochitl
echo "All EPUB files processed and sent to ReMarkable tablet"

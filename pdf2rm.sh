#!/bin/bash
# [[file:index.org::*default parameter settings][default parameter settings:1]]
REMARKABLE=${HOME}/remarkable
# default parameter settings:1 ends here

# [[file:index.org::*get PDF file information][get PDF file information:1]]
for pdf in $*
do
    if [ -f ${pdf} ]; then
        n=$(pdfinfo ${pdf} | grep '^Pages' | awk '{print $2}')
        name=$(basename ${pdf} .pdf)
        date="$(date +%s)000"
        echo Uploading PDF document ${name} with ${n} pages, date ${date}
        temp=$(mktemp --directory rm.XXXXX)
        echo Resulting documents in ${temp}
# get PDF file information:1 ends here

# [[file:index.org::uuid][uuid]]
uuid=$(uuidgen)
echo Creating $uuid document directories.
dest=${temp}/${uuid}
mkdir ${dest}
mkdir ${dest}.{cache,highlights,textconversion,thumbnails}
cp ${pdf} ${dest}.pdf
# uuid ends here

# [[file:index.org::*content file][content file:1]]
cat > ${dest}.content <<EOF
{
    "extraMetadata": {
    },
    "fileType": "pdf",
    "fontName": "",
    "lastOpenedPage": 0,
    "lineHeight": -1,
    "margins": 100,
    "orientation": "portrait",
EOF
echo '    "pageCount":' ${n}',' >> ${dest}.content
echo '    "pages": [' >> ${dest}.content
page=1
while [ ${page} -le ${n} ]
do
    pageuuid=$(uuidgen)
    if [ ${page} -ne ${n} ]
    then
        echo '        "'${pageuuid}'",' >> ${dest}.content
    else
        echo '        "'${pageuuid}'"' >> ${dest}.content
    fi
    ((page++))
done
cat >> ${dest}.content <<EOF
],
    "textScale": 1,
    "transform": {
        "m11": 1,
        "m12": 0,
        "m13": 0,
        "m21": 0,
        "m22": 1,
        "m23": 0,
        "m31": 0,
        "m32": 0,
        "m33": 1
    }
}
EOF
# content file:1 ends here

# [[file:index.org::*metadata file][metadata file:1]]
cat > ${dest}.metadata <<EOF
{
    "deleted": false,
EOF
echo '    "lastModified": "'${date}'",' >> ${dest}.metadata 
cat >> ${dest}.metadata <<EOF
    "metadatamodified": false,
    "modified": false,
    "parent": "",
    "pinned": false,
    "synced": false,
    "type": "DocumentType",
    "version": 1,
EOF
echo '    "visibleName": "'${name}'"' >> ${dest}.metadata 
echo '}' >> ${dest}.metadata
# metadata file:1 ends here

# [[file:index.org::*pagedata file][pagedata file:1]]
page=1
touch ${dest}.pagedata
while [ ${page} -le ${n} ]
do
    echo Blank >> ${dest}.pagedata
    ((page++))
done
# pagedata file:1 ends here

# [[file:index.org::*thumbnails][thumbnails:1]]
pdfseparate ${pdf} ${dest}.thumbnails/%d.pdf
page=0
while [ $page -lt $n ]
do
    convert ${dest}.thumbnails/$((page+1)).pdf -monochrome -scale 362x512 ${dest}.thumbnails/${page}.jpg
    rm ${dest}.thumbnails/$((page+1)).pdf
    ((page++))
done
# thumbnails:1 ends here

# [[file:index.org::*copy files to the tablet][copy files to the tablet:1]]
( cd ${temp} ; tar cf - . | \
      (cd ${REMARKABLE}/home/root/.local/share/remarkable/xochitl/ ; tar xvf - ))
# copy files to the tablet:1 ends here

# [[file:index.org::*clean up][clean up:1]]
rm -rf ${temp}
# clean up:1 ends here

# [[file:index.org::*end of if and loop for processing each file][end of if and loop for processing each file:1]]
fi
done
# end of if and loop for processing each file:1 ends here

# [[file:index.org::*restart =xochitl=][restart =xochitl=:1]]
REMARKABLE_IP="192.168.1.164"  # Replace with your tablet's IP or hostname
REMARKABLE_PASSWORD="KnnGR6W0MX"  # Replace with your tablet's password
sshpass -p $REMARKABLE_PASSWORD ssh root@$REMARKABLE_IP systemctl restart xochitl
# restart =xochitl=:1 ends here
echo "All PDF files processed and sent to ReMarkable tablet"


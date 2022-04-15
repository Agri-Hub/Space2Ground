
function downloadSentinel {
  mkdir -p data
  cd data
  wget https://zenodo.org/record/6458006/files/Sentinel_Data.zip
  unzip Sentinel_Data.zip
  rm Sentinel_Data.zip
  cd ..
}

function downloadStreeLevel {
  mkdir -p data/streetLevel_patches
  cd data/streetLevel_patches
  wget https://zenodo.org/record/6458006/files/StreetLevelImages.zip
  unzip StreetLevelImages.zip
  rm StreetLevelImages.zip
  cd ..
}

function downloadMapillaryAnnotated {
  mkdir -p data/Mapillary
  cd data/Mapillary
  wget https://zenodo.org/record/5846417/files/mapillary.zip
  unzip mapillary.zip
  rm mapillary.zip
  cd ..
}


if [ "$1" == "sentinel" ]; then
    downloadSentinel
elif [ "$1" == "imagepatches" ]; then
    downloadStreeLevel
elif [ "$1" == "mapillary" ]; then
    downloadMapillaryAnnotated
elif [ "$1" == "all" ]; then
    downloadSentinel
    downloadStreeLevel
    downloadMapillaryAnnotated
else
    echo "please provide 'sentinel', 'imagepatches','mapillary', or 'all' as argument"
fi

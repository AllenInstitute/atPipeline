

USAGE="$0 --owner <OWNER> --project <PROJECT>\
 --stack <STACK> --minZ <MINZ> --maxZ <MAXZ>\
 --collection <COLLECTION>\
 --renderWithFilter <RENDERWITHFILTER>\
 --maxIntensity <MAXINTENSITY> \
 --deltaZ <DELTAZ>"
export RENDERWITHFILTER=true
export MAXINTENSITY=50000
export DELTAZ=10
options=$(getopt -n $0 -l owner:,project:,stack:,minZ:,maxZ:,collection:,renderWithFilter:,deltaZ: -- v "$@")
eval set -- "$options"

while true; do
	case "$1" in
		--owner)
			shift
			OWNER=$1;;
		--project)
			shift
			PROJECT=$1;;
		--stack)
			shift
			STACK=$1;;
		--minZ)
			shift
			MINZ=$1;;
		--maxZ)
			shift
			MAXZ=$1;;
		--collection)
			shift
			COLLECTION=$1;;
		--renderWithFilter)
			shift
			RENDERWITHFILTER=$1;;
		--maxIntensity)
			shift
			MAXINTENSITY=$1;;
		--deltaZ)
			shift
			DELTAZ=$1;;
		--)
			shift
			break;;
		*)
			echo $USAGE
	esac
	shift
done
shift $((OPTIND-1))

echo owner=$OWNER
echo project=$PROJECT
echo stack=$STACK
echo minz=$MINZ
echo maxz=$MAXZ
echo collection=$COLLECTION
echo renderWithFilter=$RENDERWITHFILTER
echo maxIntensity=$MAXINTENSITY
echo deltaZ=$DELTAZ
PARALLELISM=$((($MAXZ-$MINZ)*50))
echo PARALLELISM=$PARALLELISM
export JSONDIR=/nas4/data/$PROJECT/processed/tilepairfiles1
export JSONFILE=$JSONDIR/tilepairs-dz$DELTAZ-$MINZ-$MAXZ-nostitch.json
export JSONFILEEDIT=$JSONDIR/tilepairs-$DELTAZ-$MINZ-$MAXZ-nostitch-EDIT.json
mkdir -p $JSONDIR
java -cp /pipeline/forrestrender/render-ws-java-client/target/render-ws-java-client-2.0.1-SNAPSHOT-standalone.jar \
org.janelia.render.client.TilePairClient \
--baseDataUrl http://ibs-forrestc-ux1:80/render-ws/v1 \
--owner $OWNER \
--project $PROJECT \
--stack $STACK \
--minZ $MINZ \
--maxZ $MAXZ \
--toJson $JSONFILE \
--excludeCornerNeighbors true \
--zNeighborDistance $DELTAZ \
--excludeSameSectionNeighbors true \
--xyNeighborFactor 0.01
echo $JSONFILEEDIT
rm -f $JSONFILEEDIT
cp $JSONFILE $JSONFILEEDIT
sed -i "s|render-parameters|render-parameters?removeAllOption=true\&maxIntensity=10000|g" $JSONFILEEDIT


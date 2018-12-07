export RENDERWITHFILTER=true
export DELTAZ=10
options=$(getopt -n $0 -l owner:,port:,host:,project:,stack:,minZ:,maxZ:,collection:,renderWithFilter:,renderScale:,SIFTmaxScale:,SIFTminScale:,SIFTsteps:,deltaZ: -- v "$@")
eval set -- "$options"

while true; do
	case "$1" in
		--owner)
			shift
			OWNER=$1;;
		--port)
			shift
			PORT=$1;;
 		--host)
			shift
			HOST=$1;;
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
		--renderScale)
			shift
			RENDERSCALE=$1;;
		--SIFTmaxScale)
			shift
			SIFTMAXSCALE=$1;;
		--SIFTminScale)
			shift
			SIFTMINSCALE=$1;;
		--SIFTsteps)
			shift
			SIFTSTEPS=$1;;
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
echo port=$PORT
echo host=$HOST
echo project=$PROJECT
echo stack=$STACK
echo minz=$MINZ
echo maxz=$MAXZ
echo collection=$COLLECTION
echo renderWithFilter=$RENDERWITHFILTER
echo deltaZ=$DELTAZ
echo renderScale=$RENDERSCALE
echo SIFTmaxScale=$SIFTMAXSCALE
echo SIFTminScale=$SIFTMINSCALE
echo SIFTsteps=$SIFTSTEPS
PARALLELISM=$((($MAXZ-$MINZ)*50))
echo PARALLELISM=$PARALLELISM

export JSONDIR=/mnt/data/$PROJECT/processed/tilepairfiles1
export JSONFILE=$JSONDIR/tilepairs-dz$DELTAZ-$MINZ-$MAXZ-nostitch.json
export JSONFILEEDIT=$JSONDIR/tilepairs-$DELTAZ-$MINZ-$MAXZ-nostitch-EDIT.json
mkdir -p $JSONDIR
# java -cp /shared/render/render-ws-java-client/target/render-ws-java-client-2.0.1-SNAPSHOT-standalone.jar \
# org.janelia.render.client.TilePairClient \
# --baseDataUrl http://W10DTMJ03EG6Z.corp.alleninstitute.org:8080/render-ws/v1 \
# --owner $OWNER \
# --project $PROJECT \
# --stack $STACK \
# --minZ $MINZ \
# --maxZ $MAXZ \
# --toJson $JSONFILE \
# --excludeCornerNeighbors true \
# --zNeighborDistance $DELTAZ \
# --excludeSameSectionNeighbors true \
# --xyNeighborFactor 0.01

#echo $JSONFILEEDIT
#rm -f $JSONFILEEDIT
#cp $JSONFILE $JSONFILEEDIT
#sed -i "s|render-parameters|render-parameters?removeAllOption=true\&minIntensity=0\&maxIntensity=65500\&|g" $JSONFILEEDIT
#sed -i "s|render-parameters|render-parameters?removeAllOption=true\&|g" $JSONFILEEDIT
# 
# if $RENDERWITHFILTER
# then
# 	#sed -i "s|render-parameters\?removeAllOption=true\&minIntensity=0\&maxIntensity=65500\&|g" $JSONFILEEDIT
  /usr/spark-2.0.2/bin/spark-submit \
  --conf spark.default.parallelism=$PARALLELISM \
  --driver-memory 19g \
  --executor-memory 50g \ 
  --executor-cores 44 \
  --deploy-mode cluster \
  --class org.janelia.render.client.spark.SIFTPointMatchClient \
  --name PointMatchFull \
  --master local[*] /shared/render/render-ws-spark-client/target/render-ws-spark-client-2.0.1-SNAPSHOT-standalone.jar \
 --baseDataUrl http://W10DTMJ03EG6Z.corp.alleninstitute.org:8080/render-ws/v1 \
#  --baseDataUrl http://ibs-forrestc-ux1:8988/render-ws/v1 \
  --collection $COLLECTION \
  --owner $OWNER \
  --pairJson $JSONFILEEDIT \
  --renderWithFilter $RENDERWITHFILTER \
  --maxFeatureCacheGb 40 \
  --matchModelType RIGID \
  --matchMinNumInliers 8 \
  --SIFTmaxScale $SIFTMAXSCALE \
  --SIFTminScale $SIFTMINSCALE \
  --SIFTsteps $SIFTSTEPS \
  --renderScale $RENDERSCALE
# else
# 	/pipeline/spark/bin/spark-submit\
#  --conf spark.default.parallelism=$PARALLELISM\
#  --driver-memory 19g\
#  --executor-memory 50g\
#  --executor-cores 44\
#  --deploy-mode cluster\
#  --class org.janelia.render.client.spark.SIFTPointMatchClient\
#  --name PointMatchFull\
#  --master spark://atbigdawg:6066\
#  /allen/aibs/pipeline/image_processing/volume_assembly/render-jars/production/render-ws-spark-client-standalone.jar\
#  --baseDataUrl http://ibs-forrestc-ux1:8988/render-ws/v1\
#  --collection $COLLECTION\
#  --owner $OWNER\
#  --pairJson $JSONFILEEDIT\
#  --renderWithFilter $RENDERWITHFILTER\
#  --maxFeatureCacheGb 40\
#  --matchModelType RIGID\
#  --matchMinNumInliers 8\
#  --SIFTmaxScale $SIFTMAXSCALE \
#  --SIFTminScale $SIFTMINSCALE \
#  --SIFTsteps $SIFTSTEPS \
#  --renderScale $RENDERSCALE
# fi


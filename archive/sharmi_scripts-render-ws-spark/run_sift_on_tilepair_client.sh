USAGE="$0 --owner <OWNER> --project <PROJECT>\
 --stack <STACK> --minZ <MINZ> --maxZ <MAXZ>\
 --collection <COLLECTION>\
 --renderWithFilter <RENDERWITHFILTER>\
 --deltaZ <DELTAZ>\
 --siftsteps <NUMSIFTSTEPS>\
 --jsonFile <JSONFILEEDIT>"
export RENDERWITHFILTER=true
export DELTAZ=10
options=$(getopt -n $0 -l owner:,project:,stack:,minZ:,maxZ:,collection:,renderWithFilter:,deltaZ:,siftsteps:,mininliers:,jsonFile: -- v "$@")
eval set -- "$options"

while true; do
	case "$1" in
		--owner)
			shift
			OWNER=$1;;
		--project)
			shift
			PROJECT=$1;;
		--siftsteps)
			shift
			NUMSIFTSTEPS=$1;;
		--stack)
			shift
			STACK=$1;;
		--mininliers)
                        shift
                        MININLIERS=$1;;
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
		--deltaZ)
			shift
			DELTAZ=$1;;
                --jsonFile)
                        shift
                        JSONFILEEDIT=$1;;
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
echo deltaZ=$DELTAZ
echo jsonfileedit=$JSONFILEEDIT
echo siftsteps = $NUMSIFTSTEPS
echo mininliers = $MININLIERS

PARALLELISM=$((($MAXZ-$MINZ)*50))
echo PARALLELISM=$PARALLELISM



#if $RENDERWITHFILTER
#then
	#sed -i "s|render-parameters\?removeAllOption=true\&minIntensity=0\&maxIntensity=65500\&|g" $JSONFILEEDIT
	/pipeline/spark/bin/spark-submit --conf spark.default.parallelism=$PARALLELISM --driver-memory 19g --executor-memory 50g\
 --executor-cores 44 --deploy-mode client\
 --class org.janelia.render.client.spark.SIFTPointMatchClient\
 --name PointMatchFull\
 --master spark://atbigdawg:7077\
 /pipeline/forrestrender/render-ws-spark-client/target/render-ws-spark-client-2.0.1-SNAPSHOT-standalone.jar\
 --baseDataUrl http://ibs-forrestc-ux1:80/render-ws/v1\
 --collection $COLLECTION\
 --owner $OWNER\
 --pairJson $JSONFILEEDIT\
 --renderWithFilter $RENDERWITHFILTER\
 --maxFeatureCacheGb 40\
 --matchModelType RIGID\
 --matchMinNumInliers $MININLIERS\
 --renderScale .5\
 --SIFTsteps $NUMSIFTSTEPS
#else
#	/pipeline/spark/bin/spark-submit\
# --conf spark.default.parallelism=$PARALLELISM\
# --driver-memory 19g\
# --executor-memory 50g\
# --executor-cores 44\
# --deploy-mode client\
# --class org.janelia.render.client.spark.SIFTPointMatchClient\
# --name PointMatchFull\
# --master spark://atbigdawg:7077\
# /pipeline/forrestrender/render-ws-spark-client/target/render-ws-spark-client-2.0.1-SNAPSHOT-standalone.jar\
# --baseDataUrl http://ibs-forrestc-ux1:8081/render-ws/v1\
# --collection $COLLECTION\
# --owner $OWNER\
# --pairJson $JSONFILEEDIT\
# --renderWithFilter $RENDERWITHFILTER\
# --maxFeatureCacheGb 40\
# --matchModelType RIGID\
# --matchMinNumInliers $MININLIERS\
# --renderScale .5\
# --SIFTsteps $NUMSIFTSTEPS
#fi


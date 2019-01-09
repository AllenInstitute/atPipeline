
/allen/aibs/pipeline/image_processing/volume_assembly/utils/spark/bin/spark-submit --conf spark.default.parallelism=4750 \
--driver-memory 19g --executor-memory 50g --executor-cores 44 \
--class org.janelia.render.client.spark.SIFTPointMatchClient \
--name PointMatchFull \
--master local[*] \
/allen/aibs/pipeline/image_processing/volume_assembly/render-jars/production/render-ws-spark-client-standalone.jar \
--baseDataUrl http://ibs-forrestc-ux1:8988/render-ws/v1 \
--collection M335503_Ai139_smallvol_DAPI_1_lowres_round1 --owner 6_ribbon_experiments \
--pairJson /nas5/data/M335503_Ai139_smallvol/processed/tilepairfiles1/tilepairs-10-0-95-nostitch-EDIT.json \
--renderWithFilter true --maxFeatureCacheGb 40 \
--matchModelType RIGID --matchMinNumInliers 8 --SIFTmaxScale 1.0 --SIFTminScale 0.8 \
--SIFTsteps 7 --renderScale 1.0


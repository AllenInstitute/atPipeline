
/usr/spark-2.0.2/bin/spark-submit \
--conf spark.default.parallelism=4750 \
--driver-memory 19g \
--executor-memory 50g \
--executor-cores 44 \
--class org.janelia.render.client.spark.SIFTPointMatchClient \
--name PointMatchFull \
--master local[*] \
/shared/render/render-ws-spark-client/target/render-ws-spark-client-2.0.1-SNAPSHOT-standalone.jar \
--baseDataUrl http://ibs-forrestc-ux1:8988/render-ws/v1 \
--collection M33_lowres_round1 \
--owner 6_ribbon_experiments \
--pairJson /mnt/data/M33/processed/tilepairfiles1/tilepairs-10-0-95-nostitch-EDIT.json \
--renderWithFilter true \
--maxFeatureCacheGb 40 \
--matchModelType RIGID \
--matchMinNumInliers 8 \
--SIFTmaxScale 1.0 \
--SIFTminScale 0.8 \
--SIFTsteps 7 \
--renderScale 1.0


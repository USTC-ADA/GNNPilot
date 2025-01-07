cd core/src
nvcc --shared -Xcompiler -fPIC -rdc=true aggregate.cu aggregate_sddmm.cu aggregate_gat.cu flash_partition.cu aggregate_gin.cu preprocessing.cu bin_pack.cu mm.cu mm_pipeline.cu spmm_mm_pipeline.cu spmm_mm_pipeline_new.cu spmm_mm_pipeline_final_new.cu -o libcutest.so
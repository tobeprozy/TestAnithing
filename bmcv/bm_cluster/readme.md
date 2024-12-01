- [运行示例](#运行示例)
- [接口说明](#接口说明)
- [bmcv\_cluster](#bmcv_cluster)


# 运行示例
```bash
chmod +x run.sh
./run.sh
```

# 接口说明
bmcv_cluster
=============

谱聚类。内部通过依次调用：bmcv_cos_similarity、bmcv_matrix_prune、bmcv_lap_matrix、bmcv_qr、bmcv_knn 接口实现谱聚类。

**处理器型号支持：**

该接口支持 BM1684X。


**接口形式：**

    .. code-block:: c

        bm_status_t bmcv_cluster(bm_handle_t     handle,
                                bm_device_mem_t input,
                                bm_device_mem_t output,
                                int             row,
                                int             col,
                                float           p,
                                int             min_num_spks,
                                int             max_num_spks,
                                int             num_iter_KNN,
                                int             weight_mode_KNN = 0,
                                int             num_spks = -1);


**参数说明：**

* bm_handle_t handle

  输入参数。 bm_handle 句柄。

* bm_image input

  输入参数。存放输入矩阵，其大小为 row * col * sizeof(float32)。

* bm_image output

  输出参数。存放 KNN 结果标签，其大小为 row * sizeof(int)。

* int row

  输入参数。输入矩阵的行数。

* int col

  输入参数。输入矩阵的列数。

* float p

  输入参数。用于剪枝步骤中的比例参数，控制如何减少相似性矩阵中的连接。

* int min_num_spks

  输入参数。最小的聚类数。

* int max_num_spks

  输入参数。最大的聚类数。

* int num_iter_KNN

  输入参数。KNN 算法的迭代次数。

* int weight_mode_KNN

  在SciPy库中，K-means算法的质心初始化方法, 0 表示 CONST_WEIGHT，1 表示 MT19937_SCIPY，2 表示 MT19937_CPP。默认使用 CONST_WEIGHT。

* int num_spks

  输入参数。指定要使用的特征向量数量，可用于直接控制输出的聚类数。如果未指定，则根据数据动态计算。

**返回值说明：**

* BM_SUCCESS: 成功

* 其他:失败


**格式支持：**

1、目前该接口只支持矩阵的数据类型为float。

**代码示例：**

    .. code-block:: c

        int    row             = 128;
        int    col             = 128;
        float  p               = 0.01;
        int    min_num_spks    = 2;
        int    max_num_spks    = 8;
        int    num_iter_KNN    = 2;
        int    weight_mode_KNN = 0;
        int    num_spks        = -1;
        float *input_data      = (float *)malloc(row * col * sizeof(float));
        int   *output_data     = (int *)malloc(row * max_num_spks * sizeof(int));

        struct timeval  t1, t2;
        bm_handle_t     handle;
        bm_status_t     ret = bm_dev_request(&handle, 0);
        bm_device_mem_t input, output;

        for (i = 0; i < row * col; ++i) {
            input_data[i] = (float)rand() / RAND_MAX;
        }

        ret = bm_malloc_device_byte(handle, &input, sizeof(float) * row * col);
        if (ret != BM_SUCCESS) {
            bmlib_log("CLUSTER", BMLIB_LOG_ERROR, "bm_malloc_device_byte input error\n");
            exit(-1);
        }
        ret = bm_malloc_device_byte(handle, &output, sizeof(float) * row * max_num_spks);
        if (ret != BM_SUCCESS) {
            bmlib_log("CLUSTER", BMLIB_LOG_ERROR, "bm_malloc_device_byte input error\n");
            exit(-1);
        }

        ret = bm_memcpy_s2d(handle, input, input_data);
        if (ret != BM_SUCCESS) {
            bmlib_log("CLUSTER", BMLIB_LOG_ERROR, "bm_memcpy_s2d input error\n");
            exit(-1);
        }

        printf("------Test Cluster Begin!------\n");
        gettimeofday(&t1, NULL);
        ret = bmcv_cluster(handle,
                           input,
                           output,
                           row,
                           col,
                           p,
                           min_num_spks,
                           max_num_spks,
                           num_iter_KNN,
                           weight_mode_KNN,
                           num_spks);
        gettimeofday(&t2, NULL);
        printf("bmcv_cluster TPU using time: %.2f(s)\n", TIME_COST_S(t1, t2));
        if (ret != BM_SUCCESS) {
            bmlib_log("CLUSTER", BMLIB_LOG_ERROR, "bmcv_cluster error\n");
            exit(-1);
        }

        ret = bm_memcpy_d2s(handle, output_data, output);
        if (ret != BM_SUCCESS) {
            bmlib_log("CLUSTER", BMLIB_LOG_ERROR, "bm_memcpy_d2s output error\n");
            exit(-1);
        }

        bm_free_device(handle, input);
        bm_free_device(handle, output);
        free(input_data);
        free(output_data);



import scipy
import numpy as np
import struct

GLBOAL_UNIFIED_SEED        = 42
USING_MT1377_PYTHON = False
flag_compensate_if_sign_bit_strangely_converted_due_to_sqrt = True
MUST_COPY_NO_CHANGE = True
assert MUST_COPY_NO_CHANGE==True

#https://stackoverflow.com/questions/77509605/mt19937-generator-in-c-and-numpy-generate-different-numbers
WORD_SIZE = 32  # The template argument after the type
STATE_SIZE = 624  # The next template argument (Also `len(np.random.MT19937().state['state']['key'])`)
INITIALIZATION_MULTIPLIER = 1812433253  # The last template argument
DEFAULT_SEED = 5489  # A constant

def cpp_seed_mt19937(seed = DEFAULT_SEED):
    state = np.zeros(STATE_SIZE, dtype=np.uint32)
    state[0] = seed
    for j in range(1, STATE_SIZE):
        state[j] = INITIALIZATION_MULTIPLIER * (state[j-1] ^ (state[j-1] >> (WORD_SIZE - 2))) + j
    result = np.random.MT19937()
    result.state = {'bit_generator': 'MT19937', 'state': {'key': state, 'pos': STATE_SIZE - 1}}
    result.random_raw(1)  # Start at index "STATE_SIZE-1" and advance by 1 to advance past the generated state
    assert 0,result
    return result

def QR_utest_sch_gram():
    R_ref = np.array([[2/2**0.5, 1/2**0.5,1/2**0.5],[0, 3/6**0.5,1/6**0.5],[0,0,2/3**0.5]])
    Q_ref = np.array([[1/2**0.5, 1/6**0.5,-1/3**0.5],[1/2**0.5, -1/6**0.5,1/3**0.5],[0,2/6**0.5,1/3**0.5]])
    A_try = np.array([[1.0,1.0,0.0],[1.0,0.0,1.0],[0.0,1.0,1.0]])
    Q,R = function_QR_HousHolder(A_try)
    # Q_sci, R_sci = scipy.linalg.qr(np.copy(A_try))
    # print_array("R_sci",R_sci)
    # print_array("R_ref",R_ref)

    # assert np.sum(np.abs(Q_sci-Q_ref))<1e-8
    # assert np.sum(np.abs(R_sci-R_ref))<1e-8
    flag = np.sum(np.abs(R_ref-R))< 1e-8
    if not flag: assert 0,np.sum(np.abs(R_ref-R))
    flag = np.sum(np.abs(Q_ref-Q))< 1e-8
    if not flag: assert 0,np.sum(np.abs(Q_ref-Q))
    if flag:print("[valid-QR] QR is checked")
    else: assert 0,"QR utest error"

def QR_utest_householder():
    R_ref = np.array([[2/2**0.5, 1/2**0.5,1/2**0.5],[0, 3/6**0.5,1/6**0.5],[0,0,2/3**0.5]])
    Q_ref = np.array([[1/2**0.5, 1/6**0.5,-1/3**0.5],[1/2**0.5, -1/6**0.5,1/3**0.5],[0,2/6**0.5,1/3**0.5]])

    A_try = np.array([[1.0,1.0,0.0],[1.0,0.0,1.0],[0.0,1.0,1.0]])
    Q,R = function_QR_HousHolder(np.copy(A_try))
    Q_ref, R_ref = scipy.linalg.qr(np.copy(A_try))
    flag = np.sum(np.abs(R_ref-R))< 1e-8
    if not flag: assert 0,np.sum(np.abs(R_ref-R))
    flag = np.sum(np.abs(Q_ref-Q))< 1e-8
    if not flag: assert 0,np.sum(np.abs(Q_ref-Q))
    if flag:print("[valid-QR] QR is checked")
    else: assert 0,"QR utest error"

def QR_utest2():
    R_ref = np.array([[2,1,1],[0,3,2],[0,0,5]])
    Q_ref = np.array([[1,0,0],[0,1,0],[0,0,1]])

    A_try = np.array([[2,1,1],[0,3,2],[0,0,5]])
    Q,R = function_QR_HousHolder(np.copy(A_try))
    Q_sci, R_sci = scipy.linalg.qr(np.copy(A_try))
    assert np.sum(np.abs(Q_sci-Q_ref))<1e-8
    assert np.sum(np.abs(R_sci-R_ref))<1e-8
    flag = np.sum(np.abs(Q_ref-Q))< 1e-8
    if not flag: assert 0,np.sum(np.abs(Q_ref-Q))
    flag = flag and np.sum(np.abs(R_ref-R))< 1e-8
    if not flag:
        assert 0,np.sum(np.abs(R_ref-R))
    if flag:print("[valid-QR] QRutest_2 is checked")
    else: assert 0,"QR utest_2 error"
# QR_utest2()
# QR_utest_householder()

def see(aaa2):
    aaa = np.copy(aaa2).flatten()
    print("quick search")
    for i,aaaa in enumerate(aaa):
        if np.abs(aaaa)>1e-7: print(i, aaaa)


class Cluster_Origin_Operator:
    def __init__(self, p=.01, num_spks=None, min_num_spks=2, max_num_spks=8):
        self.p = p
        self.num_spks     = num_spks
        self.min_num_spks = min_num_spks
        self.max_num_spks = max_num_spks
        assert MUST_COPY_NO_CHANGE==True

    def analysizer_sysmetric(self, input):
        assert len(input.shape)==2
        m = input.shape[0]
        n = input.shape[1]
        assert m == n
        total_num_nonzero_half_triangle = 0
        total_non_sysmetric_half_triangle = 0

        for i in range(n):
            for j in range(i + 1, n):
                right_upper = input[i][j]
                left_upper  = input[n - i - 1][n - j - 1]
                if (left_upper != 0 and right_upper !=0):
                    total_num_nonzero_half_triangle += 1
                    if (right_upper != left_upper):
                        total_non_sysmetric_half_triangle += 1
        precentage = 2*total_num_nonzero_half_triangle/(n*n)/100
        print("[parser precentage in half_triangle {}/{}={}%]".format(total_num_nonzero_half_triangle,int(n*n/2),precentage))
        print("[non-sysmetric in  half_triangle {}/{}={}%]".format(total_non_sysmetric_half_triangle,total_num_nonzero_half_triangle,total_non_sysmetric_half_triangle/total_num_nonzero_half_triangle))
        if total_non_sysmetric_half_triangle > 0:
            print("[NOT SYSMETRIC]")
        else:
            print("[IS SYSMETRIC]")


    # Define utility functions
    def cosine_similarity(self, M):
        M = M / np.linalg.norm(M, axis=1, keepdims=True)
        return 0.5 * (1.0 + np.dot(M, M.T))

    def prune(self, M):
        m = M.shape[0]
        if m < 1000:
            n = max(m - 10, 2)
        else:
            n = int((1.0 - self.p) * m)
        for i in range(m):
            indexes = np.argsort(M[i, :])
            low_indexes, high_indexes = indexes[0:n], indexes[n:m]
            M[i, low_indexes] = 0.0
            M[i, high_indexes] = 1.0
        return 0.5 * (M + M.T)

    def laplacian(self, M):
        M[np.diag_indices(M.shape[0])] = 0.0
        D = np.diag(np.sum(np.abs(M), axis=1))
        return D - M

    def spectral(self, M, num_spks, min_num_spks, max_num_spks):

        M = M
        np.copy(M).astype('float32').tofile("./ref_QR_input_M.bin")
        eig_values, eig_vectors = scipy.linalg.eigh(M.astype(dtype=np.float32))
        # # assert 0,np.sort(eig_values)[-2]
        # for i in  np.argsort(eig_values):
        #     print(i,eig_values[i])
        # for i in  np.argsort(eig_values):
        #     print(i,eig_values[i],eig_vectors[:,i])
        np.copy(eig_values).astype('float32').tofile("./ARM_eig_value.bin")
        np.copy(eig_values).astype('float32').tofile("./ref_QR_output_eig_values.bin")
        np.copy(eig_vectors).astype('float32').tofile("./ref_QR_output_eig_vectors.bin")
        num_spks = num_spks if num_spks is not None \
            else np.argmax(np.diff(eig_values[:max_num_spks + 1])) + 1
        num_spks = max(num_spks, min_num_spks)
        np.copy(eig_vectors[:, :num_spks]).astype('float32').tofile("./ARM_seelect_vector.bin")
        # assert 0,(num_spks,np.diff(eig_values[:max_num_spks + 1]),eig_vectors[:, :num_spks])
        return eig_vectors[:, :num_spks]

    def kmeans(self,data):
            k = data.shape[1]
            centroids, labels = scipy.cluster.vq.kmeans2(np.copy(data), k, minit='++', iter=2, seed=GLBOAL_UNIFIED_SEED)
            # _, labels, _ = k_means(data, k,  random_state=None, n_init=20)
            # _, labels, _ = k_means(data, k,  random_state=None, n_init='auto')
            # _, labels, _ = k_means(data, k,  init='k-means++', random_state=None, n_init='auto', algorithm='elkan')
            # clustering = AffinityPropagation(random_state=5).fit(data)
            # labels = clustering.labels_
            return labels

    def preprocess(self, path):
        input_cvte = np.loadtxt(path,dtype=np.float32)
        time_step         = input_cvte[:, 0:2]
        matrix_embeddings = input_cvte[:, 2:]
        print("[matrix_embeddings]",matrix_embeddings.shape)
        return matrix_embeddings

    def run_origin(self, embeddings_input):
        embeddings = np.copy(embeddings_input)
        # Fallback for trivial cases
        if len(embeddings) <= 2:
            return [0] * len(embeddings)

        # Compute similarity matrix
        similarity_matrix = self.cosine_similarity(np.array(embeddings))
        # Prune matrix with p interval
        pruned_similarity_matrix = self.prune(similarity_matrix)
        # Compute Laplacian
        laplacian_matrix = self.laplacian(pruned_similarity_matrix)
        # Compute spectral embeddings
        self.check_Hermitian(laplacian_matrix)
        self.analysizer_sysmetric(laplacian_matrix)
        spectral_embeddings = self.spectral(laplacian_matrix, self.num_spks, self.min_num_spks, self.max_num_spks)
        # Assign class labels
        # np.copy(spectral_embeddings[:128,:]).astype('float32').tofile("./DQ_KNN_input.bin")
        labels = self.kmeans(spectral_embeddings)
        return labels

class Cluster_Helper():
    def PRINT_FUNC(self, message):
        if self.FLOG:
            print(message)

    def check_if_real_sysmmetric(self, input_A_in):
        input_A = np.copy(input_A_in)
        assert len(input_A.shape) == 2, "only supprot shape-[n,n] style!"
        n = input_A.shape[0]
        for i in range(n):
            assert np.sum(input_A[i,:]-input_A[:,i]) < 1e-4
        print("[Valid-check] householder result is tri-real_sys matrix!")

    def check_if_real_orthogonal(self, data,tag=" tri-householder H"):
        input_A =  np.copy(data)
        assert len(input_A.shape) == 2, "only supprot shape-[n,n] style!"
        n = input_A.shape[0]
        sum_val =  np.sum(np.abs(np.eye(n)-np.matmul(input_A,input_A.T)))
        flag_is_orthogonal = sum_val < 1e-5
        if (flag_is_orthogonal):
            print("[Valid-check] {}  is vertical orthogonal".format(tag))
        else:
            print("[Warning] {}  is NOT vertical orthogonal, error:{}!".format(tag, sum_val))

    def check_if_column_orthogonal(self, data,tag=" tri-householder H"):
        input_A =  np.copy(data)
        assert len(input_A.shape) == 2, "only supprot shape-[n,n] style!"
        m = input_A.shape[1]
        for i in range(m):
            for j in range(i+1,m):
               flag_is_orthogonal =np.sum(np.abs(np.matmul(data[:,i].T,data[:,j]))) < 1e-5
        if (flag_is_orthogonal):
            print("[Valid-check] {}  is vertical orthogonal".format(tag))
        else:
            print("[Warning] {}  is NOT vertical orthogonal!".format(tag))

    def check_if_unitary(self, data,tag=" tri-householder H"):
        input_A =  np.copsy(data)
        assert len(input_A.shape) == 2, "only supprot shape-[n,n] style!"
        n = input_A.shape[0]
        m = input_A.shape[1]
        n_flag_is_orthogonal =  np.sum(np.abs(np.eye(n)-np.matmul(input_A,input_A.T)))< 1e-2
        m_flag_is_orthogonal =  np.sum(np.abs(np.eye(m)-np.matmul(input_A.T,input_A)))< 1e-2
        if (n_flag_is_orthogonal + m_flag_is_orthogonal):
            print("[Valid-check] {}  is unitary".format(tag))
        else:
            print("[Warning] {}  is NOT unitary!".format(tag))

    def check_if_real_trisadiagonal_sysmmetric(self, input_A_in, input_A_origin, H_cascade):
        input_A = np.copy(input_A_in)
        n = input_A.shape[0]
        assert np.sum(np.abs(np.triu(input_A,2)))  < 1e-2,np.sum(np.abs(np.triu(input_A,2)))
        assert np.sum(np.abs(np.tril(input_A,-2))) < 1e-2
        for i in range(1, n):
            assert (input_A[i][i-1]-input_A[i-1][i])<1e-2,(input_A[i][i-1],input_A[i-1][i])
        assert np.sum(np.abs(input_A -  np.matmul(np.matmul(H_cascade, input_A_origin),H_cascade.T) ))<1e-1,np.sum(np.abs(input_A -  np.matmul(np.matmul(H_cascade, input_A_origin),H_cascade.T) ))
        print("[Valid-check]input is real_tridiagonal_sysmmetric")

    def transform2diag(self, input_A):
            assert len(input_A.shape)==1
            return np.diag(input_A)

    def print_array(self, tag,input_A):
        print(tag,":",np.array_str(input_A, precision=2, suppress_small=True))

    def check_Hermitian(self, M):
        self.check_if_real_sysmmetric(M)


class Cluster_Reproductor(Cluster_Origin_Operator, Cluster_Helper):
    FLOG           = False

    precision_iter = 6
    AROUND_BIT     = 16

    def __init__(self, p=.01, num_spks=None, min_num_spks=2, max_num_spks=8):
        Cluster_Helper.__init__(self)
        Cluster_Origin_Operator.__init__(self,p, num_spks, min_num_spks, max_num_spks)
        assert MUST_COPY_NO_CHANGE==True
        assert self.AROUND_BIT    >= 8
        assert isinstance(self.AROUND_BIT, int)
        assert isinstance(self.precision_iter, int)
        assert isinstance(flag_compensate_if_sign_bit_strangely_converted_due_to_sqrt, bool)
        print("<---------------[BasicInfo]-------------->")
        print("precision_iter:{}".format(self.precision_iter))
        if flag_compensate_if_sign_bit_strangely_converted_due_to_sqrt:
            print("[Warning]rough l2-compute is on!")
            print("AROUND_BIT:{}".format(self.AROUND_BIT))
        print("--------------------------------------------")


    #https://betterexplained.com/articles/understanding-quakes-fast-inverse-square-root/
    def fast_inverse_sqrt(self, number):
            assert not isinstance(number ,np.ndarray)
            assert number >0, number
            x = float(number)
            i = struct.unpack('i', struct.pack('f', x))[0]
            i = 0x5F3759DF - (i >> 1)

            y = struct.unpack('f', struct.pack('i', i))[0]
            # Use Newton's method to refine the estimate
            C_1_5 = float(1.5)
            C_0_5 = float(0.5)
            half_x = C_0_5 * x
            for i in range(4):
                y = y * (C_1_5 - half_x * y * y)
            y = np.array(y ,dtype=np.float32)
            return y

    def fast_sqrt(self, value):
        return value * self.fast_inverse_sqrt(value)

    def fast_div(self, a, b):
        sign = 0
        if b > 0: sign = 1.0
        if b < 0: sign = -1.0
        temp_b = self.fast_inverse_sqrt(np.abs(b))
        return a * sign * ( temp_b* temp_b)

    def l2_norm(self, x):
        if flag_compensate_if_sign_bit_strangely_converted_due_to_sqrt== True:
            tmp =  self.fast_sqrt(np.sum(x*x))
        else:
            tmp =  np.sqrt(np.sum(x*x))
        # if flag_compensate_if_sign_bit_strangely_converted_due_to_sqrt== True:
        #     tmp = np.around(tmp, self.AROUND_BIT)
        return tmp
    #a/norm_2(b)**2
    #=>a/sum(b*b)
    def fast_div_l2_norm_power2(self ,a ,b):
        revised_tmp = np.sum(b * b)
        return a * self.fast_div(float(1.0), revised_tmp)

    def standard_euclidean(self, p1, p2):
        result = []
        for i in range(p1.shape[0]):
           result +=[np.sqrt(np.sum((p1[i,:].reshape([1,p2.shape[-1]]) - p2)**2, axis=1))]
        result = np.stack(result).reshape([p1.shape[0],p2.shape[-1]])
        result_tpu = []
        for i in range(p2.shape[0]):
           result_tpu +=[np.sqrt(np.sum((p2[i,:].reshape([1,p2.shape[-1]]) - p1)**2, axis=1))]
        result_tpu = np.stack(result_tpu, axis=1).reshape([p1.shape[0],p2.shape[-1]])
        return  result

    def sqeuclidean(self,  p1, p2):
        result = []
        for i in range(p1.shape[0]):
           result +=[np.sum((p1[i,:].reshape([1,p2.shape[-1]]) - p2)**2, axis=1)]
        result = np.stack(result).reshape([p1.shape[0],p2.shape[0]])
        return  result

    def function_QR_Gram_Schmidt(self, matrix_tri):
        n= matrix_tri.shape[0]
        e_list = []
        for k in range(0, n):
          a_k = matrix_tri[:,k]
          u_k = np.copy(a_k)
          for j in range(k):
              scalar = np.matmul(a_k.reshape(1,n),e_list[j].reshape(n ,1)).flatten()[0]
              u_k = u_k- scalar *np.array(e_list[j])
          if self.l2_norm(u_k)>0:
              e_list += [u_k/self.l2_norm(u_k)]
          else:
              e_list += [u_k]
        # assert 0,u_i
        Q = np.zeros([n,n])
        R = np.zeros([n,n])
        for i in range(n):
                Q[:,i]  = e_list[i].reshape(n)
        for i in range(n):
            for j in range(i, n):
                print("R-{}-{} = a{}*e{}".format(i,j,j,i))
                R[i, j] = np.matmul(matrix_tri[:, j].reshape(1,n), e_list[i].reshape(n ,1))
        assert 0
        print("------------------------------------------------")
        self.print_array('matrix_tri',matrix_tri)
        self.print_array('matmul(Q,R)',np.matmul(Q,R))
        self.print_array('Q',Q)
        self.print_array('R',R)

        assert np.sum(np.abs(np.copy(matrix_tri)- np.matmul(Q,R)))<1e-8,np.sum(np.abs(matrix_tri- np.matmul(Q,R)))
        return Q, R

    def function_QR_HousHolder(self, matrix_tri):
        matrix_tri_origin = np.copy(matrix_tri)
        n = matrix_tri.shape[0]
        R = np.copy(matrix_tri) if MUST_COPY_NO_CHANGE else matrix_tri
        Q = 1.0*np.eye(n)
        def tau_householder(a):
            v = np.copy(a) if MUST_COPY_NO_CHANGE else a
            yita = np.matmul(v[1:].T,v[1:])
            if flag_compensate_if_sign_bit_strangely_converted_due_to_sqrt==False:
                if yita==0.0:
                    return 0,v.reshape([-1,1])

            if flag_compensate_if_sign_bit_strangely_converted_due_to_sqrt==True:
                alpha = self.fast_sqrt(v[0]* v[0] + yita)
                # alpha = np.around(alpha, self.AROUND_BIT)
            else:
                alpha = np.sqrt(v[0]**2 + yita)
            s  =  1 if  v[0] >=0 else -1
            v[0] =  v[0] + s*alpha
            if flag_compensate_if_sign_bit_strangely_converted_due_to_sqrt==True:
                tau = self.fast_div(2.0, v[0] * v[0]+yita)
            else:
                tau = 2/(v[0] **2+yita)

            v = v.reshape([-1,1])
            return tau,v

        # for jj in range(n-1):
        #     a = R[jj:,jj]
        #     tau,w = tau_householder(a)
        #     R[jj:,jj:] = R[jj:, jj:] - tau*np.matmul(w ,np.matmul(w.T, R[jj:,jj:]))
        #     Q[:, jj:] = Q[:,  jj:] - tau*np.matmul(np.matmul(Q[:, jj:],w) ,w.T)
        for j in range(n-1):
            a = R[j:,j]
            tau,w = tau_householder(a)
            self.PRINT_FUNC("jj:{} tau:{} w:{} a:{}, R:{}".format(j, tau, w ,a,R))
            # assert 0,(tau.shape, w.shape,R[j:, :].shape)
            R[j:,j:] = R[j:, j:] - tau*np.matmul(w ,np.matmul(w.T, R[j:,j:]))

            self.PRINT_FUNC("after R: {}".format(R))
            Q[:, j:] = Q[:,  j:] - tau*np.matmul(np.matmul(Q[:, j:],w) ,w.T)
            self.PRINT_FUNC("Q:{}".format(Q))
            self.PRINT_FUNC("----------------------")
        assert np.sum(np.abs(matrix_tri_origin - np.matmul(Q,R)))<5e-3,np.sum(np.abs(matrix_tri_origin - np.matmul(Q,R)))
        return Q,R

    # def function_QR_HousHolder_new_version(self, matrix_tri):
    #     matrix_tri_origin = np.copy(matrix_tri)
    #     n = matrix_tri.shape[0]
    #     R = np.copy(matrix_tri) if MUST_COPY_NO_CHANGE else matrix_tri
    #     Q = 1.0*np.eye(n)
    #     def tau_householder(a):
    #         v = np.copy(a) if MUST_COPY_NO_CHANGE else a
    #         yita = np.matmul(v[1:].T,v[1:])
    #         if flag_compensate_if_sign_bit_strangely_converted_due_to_sqrt==False:
    #             if yita==0:
    #                 return 0,v.reshape([-1,1])

    #         if flag_compensate_if_sign_bit_strangely_converted_due_to_sqrt==True:
    #             alpha = self.fast_sqrt(v[0]* v[0] + yita)
    #             # alpha = np.around(alpha, self.AROUND_BIT)
    #         else:
    #             alpha = np.sqrt(v[0]**2 + yita)
    #         v[0] = v[0] - alpha if v[0] <= 0 else -yita / (v[0] + alpha)
    #         if flag_compensate_if_sign_bit_strangely_converted_due_to_sqrt==True:
    #             tau = self.fast_div(2.0, v[0] * v[0]+yita)
    #         else:
    #             tau = 2 * v[0]**2 / (yita + v[0]**2)
    #         v = v.reshape([-1,1])/v[0]
    #         return tau,v

    #     # for jj in range(n-1):
    #     #     a = R[jj:,jj]
    #     #     tau,w = tau_householder(a)
    #     #     R[jj:,jj:] = R[jj:, jj:] - tau*np.matmul(w ,np.matmul(w.T, R[jj:,jj:]))
    #     #     Q[:, jj:] = Q[:,  jj:] - tau*np.matmul(np.matmul(Q[:, jj:],w) ,w.T)
    #     for j in range(n):
    #         a = R[j:,j]
    #         tau,w = tau_householder(a)
    #         self.PRINT_FUNC("jj:{} tau:{} w:{} a:{}, R:{}".format(j, tau, w ,a,R))
    #         # assert 0,(tau.shape, w.shape,R[j:, :].shape)
    #         H = np.identity(n)
    #         H[j:, j:] -= tau * w.reshape(-1, 1) @ w.reshape(1,-1)
    #         R = H @ R
    #         Q = H @ Q

    #     return Q[:n].T, R[:n]

    def spectral_sophon(self, M):
        assert 0, "[Error]Prohibited use"
        np.copy(M).astype('float32').tofile("./DQ_QR_input_M.bin")
        eig_values_sophon, eig_vectors_sophon = self.function_real_sysmmetric_matrix_eign_solver(M)
        eig_values, eig_vectors = scipy.linalg.eigh(M)
        R_tpu_eignvalue_vector = np.fromfile("../nntoolchain/TPU1686/R_tpu_eignvalue_vector.dat",dtype=np.float32)
        # assert np.sum(np.abs(eig_values_sophon- eig_values)) <1e-4

        np.copy(eig_values_sophon).astype('float32').tofile("./DQ_QR_output_eig_values.bin")
        np.copy(eig_vectors_sophon).astype('float32').tofile("./DQ_QR_output_eig_vectors.bin")
        np.copy(eig_values).astype('float32').tofile("./ref_QR_output_eig_values.bin")
        np.copy(eig_vectors).astype('float32').tofile("./ref_QR_output_eig_vectors.bin")
        assert 0,(eig_values_sophon,R_tpu_eignvalue_vector)

        # assert 0,(eig_values_sophon, eig_values)
        idx_eig_values_sophon_rank = np.argsort(eig_values_sophon)
        eig_values_sophon_rank  = eig_values_sophon[idx_eig_values_sophon_rank]
        eig_vectors_sophon_rank = eig_vectors_sophon[idx_eig_values_sophon_rank]
        eig_values_rank     = np.sort(eig_values)
        sort_error_eignvalues  = np.sum(np.abs(eig_values_sophon_rank- eig_values_rank))/eig_values_sophon_rank.shape[0]
        sort_error_eignvectors = np.sum(np.abs(eig_vectors_sophon- eig_vectors))/eig_vectors_sophon.shape[0]**2
        assert sort_error_eignvalues < 1, ("\n",eig_values_sophon_rank, "\n",eig_values_rank)
        # assert 0,(eig_vectors_sophon, eig_vectors)
        # assert 0,(eig_values_sophon, eig_values)
        assert sort_error_eignvectors < 1,(eig_vectors_sophon, eig_vectors)#eig_vectors_sophon_rank, eig_values_rank)
        n = M.shape[0]
        for i in range(n):
            AX =  np.matmul(M, eig_vectors_sophon[:,i].reshape(n,1))
            lamdaX =   eig_values_sophon[i]*np.matmul(np.diag(np.ones(n)), eig_vectors_sophon[:,i].reshape(n,1))
            sum_AX_lamdaX = np.sum(np.abs(np.matmul(M, eig_vectors_sophon[:,i].reshape(n,1)) -  eig_values_sophon[i]*np.matmul(np.diag(np.ones(n)), eig_vectors_sophon[:,i].reshape(n,1))))

            if flag_compensate_if_sign_bit_strangely_converted_due_to_sqrt==False:
                if sum_AX_lamdaX>1e-3:
                    print("AX",AX)
                    print("lamdaX",lamdaX)
                    print("see {}-sum-{}".format(i,sum_AX_lamdaX),lamdaX - AX)
                    assert  0,(i,sum_AX_lamdaX)
            else:
                if sum_AX_lamdaX>1e-2:
                    assert  0,(i,sum_AX_lamdaX)
        # assert 0, np.sum(np.abs(np.matmul(M, eig_vectors_sophon[:,0].reshape(n,1)) -  eig_values_sophon[0]*np.matmul(np.diag(np.ones(n)), eig_vectors_sophon[:,0].reshape(n,1))))
        # assert 0, np.sum(np.abs(np.matmul(M, eig_vectors[:,0].reshape(n,1))    -  eig_values[0]* np.matmul( np.diag(np.ones(n)), eig_vectors[:,0].reshape(n,1))))
        # assert 0, np.sum(np.abs(np.matmul(M, eig_vectors_sophon) -  np.matmul(transform2diag(eig_values_sophon), eig_vectors_sophon)))
        num_spks = num_spks if self.num_spks is not None \
            else np.argmax(np.diff(eig_values[:self.max_num_spks + 1])) + 1
        # assert 0,(num_spks,self.min_num_spks)
        num_spks = max(num_spks, self.min_num_spks)
        # assert 0,"cmp safe"
        return eig_vectors[:, :num_spks]

    def _kpp_sophon(self, data, k, rng):
        dims = data.shape[1] if len(data.shape) > 1 else 1
        init = np.ndarray((k, dims))
        for i in range(k):
            if i == 0:
                ##rng_integers  (RandomState(MT19937) at 0x7F3C32043440, 2164, None)
                if USING_MT1377_PYTHON:
                    assert 0,(rng.randint(data.shape[0]),rng,data.shape[0])
                    init[i, :] = data[rng.randint(data.shape[0])]
                else:
                    fake_rng_randint = int(data.shape[0]/2)
                    init[i, :] = data[fake_rng_randint]

            else:
                print("[Sophon Info]",init[:i,:].shape, data.shape)
                #D2 = cdist(init[:i,:], data, metric='sqeuclidean').min(axis=0) #sqeuclidean is norm_2**2
                D2  = self.sqeuclidean(init[:i,:], data).min(axis=0)
                probs = D2/D2.sum()
                cumprobs = probs.cumsum()
                r = rng.uniform()
                fake_r =np.min(cumprobs) + (np.max(cumprobs)- np.min(cumprobs))/2
                if not USING_MT1377_PYTHON:
                    r = fake_r
                # init[i, :] = data[np.searchsorted(cumprobs, r)]
                # assert i!=7,(i,init[:i, :],init[:i, :].shape)
                init[i, :] = data[np.searchsorted(cumprobs, r)]
        return init


    def py_vq_sophon(self, obs, code_book, check_finite=True):
        if obs.ndim != code_book.ndim:
            raise ValueError("Observation and code_book should have the same rank")
        if obs.ndim == 1:
            obs = obs[:, np.newaxis]
            code_book = code_book[:, np.newaxis]
        dist = self.standard_euclidean(obs, code_book)
        code = dist.argmin(axis=1)#every code element < code_book.shape[-1] == obs.shape[-1]
        min_dist = dist[np.arange(len(code)), code]
        return code, min_dist

    def  sophon_update_cluster_means(self, obs, labels, nc):
        if obs.ndim == 1:
            nfeat = 1
            cb = np.zeros(nc, dtype=obs.dtype)
        elif obs.ndim == 2:
            nfeat = obs.shape[1]
            cb = np.zeros((nc, nfeat), dtype=obs.dtype)
        else:
            raise ValueError('ndim different than 1 or 2 are not supported')
        nobs = obs.shape[0]
        # Calculate the sums the numbers of obs in each cluster
        obs_count = np.zeros(nc, np.intc)
        cb_fake = np.copy(cb)
        obs_p = np.copy(obs)
        for i in range(nobs):
            label = labels[i]
            # for j in range(nfeat):
            #     cb[label, j] += obs_p[i, j]
            cb[label, :] +=  obs_p[i, :]
            # Count the obs in each cluster
            obs_count[label] += 1
        # cb[labels[i], :]     +=  obs_p[i, :]
        # obs_count[labels[i]] += 1
        #used-for-tpu simulation
        for i in range(obs.shape[1]):
            i_group = np.array(np.where(labels==i)[0])
            cb_fake[i,:] = np.sum(obs_p[i_group],axis=0)
            cb_fake[i,:] = cb_fake[i,:]/i_group.shape[0]
        for i in range(nc):
            cluster_size = obs_count[i]
            if cluster_size > 0:
                # Calculate the centroid of each cluster
                for j in range(nfeat):
                    cb[i,j] /= cluster_size
        assert np.sum(np.abs(cb_fake-cb ))<1e-9
        # Return a boolean array indicating which clusters have members
        return cb, obs_count > 0

    def _tri_transformer(self, matrix_input):
        matrix_tri = np.copy(matrix_input )
        n = matrix_tri.shape[0]
        for i in range(0, n - 2 ):
            print("tri-step {}".format(i))

            x = matrix_tri[i+1:n,i]
            #e1 defined as [1, 0,0...0]
            e1 = np.zeros(x.shape[0])
            e1[0] = 1.0
            sign = 1.0 if x[0]>=0 else -1
            u = x + sign*e1*self.l2_norm(x)
            u = u.reshape([x.shape[0],1])
            # if i==1:
            #     assert 0,(i, self.l2_norm(x),x)
            if 1 or (self.l2_norm(u)>0):
                # assert 0,(matrix_tri[i+1:n, 0:n],2 * np.matmul(u, np.matmul(u.T, matrix_tri[i+1:n, 0:n]))/l2_norm(u)**2)
                # assert 0,(matrix_tri[i+1:n, 0:n])
                # assert 0,(np.matmul(u, np.matmul(u.T, matrix_tri[i+1:n, 0:n]))).reshape(-1,4)[0:32,:]

                # assert 0,(2 * np.matmul(u, np.matmul(u.T, matrix_tri[i+1:n, 0:n]))/l2_norm(u)**2).reshape(-1,4)[0:32,:]
                # assert i!=2,matrix_tri[2]
                # assert 0,l2_norm(u)**2
                # assert 0, ( np.matmul(u, np.matmul(u.T, matrix_tri[i+1:n, 0:n]))).flatten()[512*0: 512*1].reshape([-1,4])
                # ttemp =2 *np.matmul(u, np.matmul(u.T, matrix_tri[i+1:n, 0:n]))/l2_norm(u)**2
                # assert 0, (ttemp.flatten()[0:128],np.sum(ttemp),2/l2_norm(u)**2)
                # assert i!=0,(ttemp.flatten()[3*128 + 89*128])
                # assert i!=0,(matrix_tri.flatten()[2 + 3*128 + 89*128])
                # assert i!=1,matrix_tri[92]
                # aaae21= 2 * np.matmul(u, np.matmul(u.T, matrix_tri[i+1:n, 0:n]))/self.l2_norm(u)**2
                # assert i!=1,aaae21[:,0:16][92-(i+1),:]#[92-(i+1)]

                if flag_compensate_if_sign_bit_strangely_converted_due_to_sqrt==True:
                    tmp = self.fast_div_l2_norm_power2(2 * np.matmul(u, np.matmul(u.T, matrix_tri[i+1:n, 0:n])), u)
                    matrix_tri[i+1:n, 0:n] = matrix_tri[i+1:n, 0:n]  - tmp
                else:
                    matrix_tri[i+1:n, 0:n] = matrix_tri[i+1:n, 0:n]  -2 * np.matmul(u, np.matmul(u.T, matrix_tri[i+1:n, 0:n]))/self.l2_norm(u)**2

                # assert i!=0,matrix_tri[1]
                # assert 0,u
                # assert i!=0,(matrix_input.flatten()[512*0: 512*1].reshape([-1,4]))
                #x /32fw tpu_global_mem_addr(glb_matrix_A + 2*4 + 3*128*4 + 25*128*4 +64*128*4)
                # assert i!=1,matrix_tri[92]

                # assert i!=1,matrix_tri[0:n, i+1:n][92]
                # assert i!=1,np.matmul(matrix_tri[0:n, i+1:n], u).flatten()[90:]

                if flag_compensate_if_sign_bit_strangely_converted_due_to_sqrt==True:
                    tmp = self.fast_div_l2_norm_power2(2 * np.matmul(np.matmul(matrix_tri[0:n, i+1:n], u), u.T), u)
                    matrix_tri[0:n, i+1:n] = matrix_tri[0:n, i+1:n]  -tmp
                else:
                    matrix_tri[0:n, i+1:n] = matrix_tri[0:n, i+1:n]  -2 * np.matmul(np.matmul(matrix_tri[0:n, i+1:n], u), u.T)/self.l2_norm(u)**2
                # print(" see ",i)
                # tag_i = 3
                # if i==tag_i:
                #     for kk in range(64*64):
                #         if kk < 64*64:
                #             if np.abs(matrix_tri.flatten()[kk] - fake_matrix_tri[kk]) > 1e-5:
                #                 print(i,kk, "{:.10f}".format(matrix_tri.flatten()[kk]), fake_matrix_tri[kk])

                # assert i!=tag_i,np.sum(np.abs(matrix_tri.flatten() - fake_matrix_tri))

            # else:
            #     assert 0,(u,x,i,n,matrix_tri)
            Holder_init = np.diag(np.ones([n]))
            if (self.l2_norm(u)>0):
                if flag_compensate_if_sign_bit_strangely_converted_due_to_sqrt== True:
                    tmp = self.fast_div_l2_norm_power2(2*np.matmul(u,u.T), u)
                    Holder_init[-x.shape[0]:,-x.shape[0]:] = np.diag(np.ones([x.shape[0]]))-tmp
                else:
                    Holder_init[-x.shape[0]:,-x.shape[0]:] = np.diag(np.ones([x.shape[0]]))-2*np.matmul(u,u.T)/self.l2_norm(u)**2
            if i==0:
                H_cascade = Holder_init
            else:
                H_cascade = np.matmul(Holder_init, H_cascade) #H4H3H2  from #H0,H1,H2,H3
        self.check_if_real_tridiagonal_sysmmetric(matrix_tri,matrix_input,H_cascade)
        self.check_if_real_orthogonal(H_cascade)
        return matrix_tri,H_cascade

    def function_real_sysmmetric_matrix_eign_solver(self, matrix_input):

        matrix_tri = np.copy(matrix_input)
        matrix_tri, H_cascade = self._tri_transformer(matrix_tri)
        n = matrix_tri.shape[0]

        # for i in range(64*64):
        #     if i < 64*64:
        #         if np.abs(matrix_tri.flatten()[i] - fake_matrix_tri[i]) > 1e-4:
        #             print(i, matrix_tri.flatten()[i], fake_matrix_tri[i])
        # assert 0,np.sum(np.abs(matrix_tri.flatten() - fake_matrix_tri))
        # for i in range(64*64):
        #     if i < 64*64:
        #         if np.abs( np.array(fake_tri_out).flatten()[i] - np.array(matrix_tri).flatten()[i]) > 1e-4:
        #             print(i,  np.array(fake_tri_out).flatten()[i], np.array(matrix_tri).flatten()[i])
        # assert 0,np.sum(np.abs(np.array(fake_tri_out).flatten() - np.array(matrix_tri).flatten()))

        # assert 0,matrix_tri[2]
        matrix_A = np.copy(matrix_tri)
        X = np.diag(np.ones([n]))
        for j in range(n-1, -1, -1):
            print("j:",j)
            for _ in range(self.precision_iter):
                s = matrix_A[j,j]
                I_j = np.diag(np.ones(j+1))
                A_shift = matrix_A[0:j+1, 0:j+1] - s*I_j

                safe_A_shift = np.copy(A_shift) if MUST_COPY_NO_CHANGE else A_shift
                Q_sophon,R_sophon = self.function_QR_HousHolder(safe_A_shift)
                # assert j!=30 ,Q_sophon[24]
                self.PRINT_FUNC("j:{},_:{},Q:{}".format(j, _, Q_sophon))
                # assert j!=0,(Q_sophon,R_sophon)
                # Q_sophon,R_sophon = scipy.linalg.qr(np.copy(A_shift))
                # if j==0 and _==iter_user-1:
                #         Q_sci,R_sci = scipy.linalg.qr(np.copy(A_shift))
                #         print("[Last-Check] Q_sci vs Q_sophon: {}".format(np.sum(np.abs(Q_sophon-Q_sci))))
                #         print("[Last-Check] R_sci vs R_sophon: {}".format(np.sum(np.abs(R_sophon-R_sci))))
                # # assert np.sum(np.abs(np.copy(A_shift)- np.matmul(Q_sci,R_sci)))<1e-8,np.sum(np.abs(A_shift- np.matmul(Q_sci,R_sci)))
                # print("QR-{}-{}-checked,Q_diff is {},,R_diff is {}".format(_,j,np.sum(np.abs(Q_sci-Q_sophon)),np.sum(np.abs(R_sci-R_sophon))))
                Q = Q_sophon
                R = R_sophon
                # if (j==2 and (_==5)):
                #     assert 0,Q
                # Q = Q_sci
                # R = R_sci
                assert Q.shape[0]==j+1, Q.shape[0]

                matrix_A[0:j+1, 0:j+1] = np.matmul(R,Q)+ s*I_j
                fake_X = np.zeros([n,n])
                fake_X[Q.shape[0]:,Q.shape[0]:] = np.eye(n-Q.shape[0])*1.0 #np.diag(np.ones(n-Q.shape[0]))
                fake_X[0:Q.shape[0],0:Q.shape[0]] = Q
                X = np.matmul(X, fake_X)
        eig_values_scipy, eig_vectors_scipy = scipy.linalg.eigh(matrix_input)
        eignvalue_diag   = np.copy(matrix_A)
        eignvalue_asvector = eignvalue_diag.diagonal()
        eignvector      = np.copy(X)
        print("-------------[Print Necessary CMP Result for householder QR]------------------")
        print("[Check-tri][housholder2tri tri =HInH.T] {}".format( np.sum(np.abs(matrix_tri -  np.matmul(np.matmul(H_cascade, matrix_input),H_cascade.T) ))))
        print("[Check-QR][tri-diag tri=XAX.T] {}".format(np.sum(np.abs(matrix_tri - np.matmul(np.matmul(X, eignvalue_diag), X.T)))))
        eig_values_scipy = np.diag(eig_values_scipy)
        print("[Check-QR][scipy   In =X'AX'.T] {}".format(np.sum(np.abs(matrix_input - np.matmul(np.matmul(eig_vectors_scipy, eig_values_scipy), eig_vectors_scipy.T)))))
        origin_eignvalue_asvector = eignvalue_asvector
        H_cascade_inverse = H_cascade.T #orthogonal
        origin_eignvector = np.matmul(H_cascade_inverse, eignvector)
        print("[Final-Check origin_sparse In =HXA(HX).T] {}".format(np.sum(np.abs(matrix_input - np.matmul(np.matmul(origin_eignvector, eignvalue_diag), origin_eignvector.T)))))
        print("-------------------------------------------------------------------------------")
        # for _, data in enumerate(H_cascade_inverse):
        #     print(data)
        # print("-------------------------------------------------------------------------------")
        # for _, data in enumerate(eignvector):
        #     print(data)
        # print("-------------------------------------------------------------------------------")
        # for _, data in enumerate(origin_eignvector):
        #     print(data)
        # print("-------------------------------------------------------------------------------")
        return origin_eignvalue_asvector,origin_eignvector

    def arnoldi_iteration(self,A, real_m: int):
        n = real_m -1
        """Compute a basis of the (n + 1)-Krylov subspace of the matrix A.

        This is the space spanned by the vectors {b, Ab, ..., A^n b}.

        Parameters
        ----------
        A : array_like
            An m × m array.
        b : array_like
            Initial vector (length m).
        n : int
            One less than the dimension of the Krylov subspace, or equivalently the *degree* of the Krylov space. Must be >= 1.

        Returns
        -------
        Q : numpy.array
            An m x (n + 1) array, where the columns are an orthonormal basis of the Krylov subspace.
            exacly n x m here, the V
        h : numpy.array
            An (n + 1) x n array. A on basis Q. It is upper Hessenberg.
            exacly m x m here, the T
        """
        b = np.ones(A.shape[0])
        eps = 1e-12
        h = np.zeros((n + 1, n))
        Q = np.zeros((A.shape[0], n + 1))
        # Normalize the input vector
        Q[:, 0] = b / np.linalg.norm(b, 2)  # Use it as the first Krylov vector
        for k in range(1, n + 1):
            v = np.dot(A, Q[:, k - 1])  # Generate a new candidate vector
            for j in range(k):  # Subtract the projections on previous vectors
                h[j, k - 1] = np.dot(Q[:, j].conj(), v)
                v = v - h[j, k - 1] * Q[:, j]
            h[k, k - 1] = np.linalg.norm(v, 2)
            if h[k, k - 1] > eps:  # Add the produced vector to the list, unless
                Q[:, k] = v / h[k, k - 1]
            else:  # If that happens, stop iterating.
                return Q, h
        return Q, h

    def _tri_lanczos(self,matrix_input, m):
        matrix_A = np.copy(matrix_input)
        n = matrix_A.shape[0]
        v_next = np.ones(n) / np.sqrt(n)
        v_prev = np.zeros(n)
        beta = np.zeros(m+1)
        beta[0] = 0
        alpha = np.zeros(m)
        V = np.zeros((n, m))
        for i in range(0, m):
            v_next_expr = v_next.reshape(n, 1)

            w = np.matmul(matrix_A, v_next_expr).reshape(n)

            alpha[i] = np.dot(w, v_next)
            w = w - alpha[i] * v_next - beta[i] * v_prev

            # Orthogonalize:
            for t in range(i):
                tmpa = np.dot(w, V[:, t])
                w -= tmpa * V[:, t]

            beta[i+1] = np.linalg.norm(w, 2)
            # print("beta git",beta[i+1],np.sqrt(np.sum(np.abs(w*w))),self.l2_norm(w))

            v_prev = v_next
            v_next = w / beta[i+1]
            V[:, i] = v_prev
        tridiag = np.diag(alpha)
        for i in range(0, m-1):
            tridiag[i, i+1] = beta[i+1]
            tridiag[i+1, i] = beta[i+1]
        self.check_if_column_orthogonal(V, "tri-lanczos V_github")
        self.check_if_unitary(V, "tri-lanczos V_github")


        v_j= np.ones(n).reshape([n,1])/self.l2_norm(np.ones(n))
        v_j_sub_1 = np.zeros([n,1])
        matrix_T = np.zeros([m,m])
        matrix_V= np.zeros([n,m])
        belta   =0
        for j in range(0, m):
            w        = np.matmul(matrix_A, v_j)
            alpha    = np.matmul(w.T, v_j)
            w        = w - alpha *  v_j - belta * v_j_sub_1
            for t in range(j):
                tmp_w = np.matmul(w.T, matrix_V[:,t])
                w -= tmp_w * matrix_V[:,t].reshape([-1,1])
            belta  = self.l2_norm(w.flatten())
            # print("beta",j,belta,np.sqrt(np.sum(np.abs(w*w))),self.l2_norm(w))
            v_j_sub_1 = np.copy(v_j)
            v_j        = w/belta
            matrix_V[: , j] = v_j_sub_1.flatten()
            matrix_T[j,   j]    = alpha
            if (j +1 <m):
                matrix_T[j,   j+1]  = belta
                matrix_T[j+1, j]    = belta
        # matrix_V= np.stack(list_v,axis=0).reshape([-1,m])
        self.check_if_column_orthogonal(matrix_V, "tri-lanczos V")
        self.check_if_unitary(matrix_V, "tri-lanczos V")
        return matrix_T,matrix_V,tridiag,V

    def function_lanczos(self, matrix_input, m):
        matrix_A = np.copy(matrix_input)
        n = matrix_A.shape[0]
        assert(m >= 2)
        matrix_T,matrix_V,tridiag, V = self._tri_lanczos(matrix_A, m)

        # assert np.sum(np.abs(tridiag-matrix_T))<1e-3, np.sum(np.abs(tridiag-matrix_T))

        H_cascade = np.copy(matrix_V)
        X         = np.diag(np.ones([m]))
        print("-------------[Print Necessary CMP Result for lanczos tri]------------------")
        if( m == n ):
                tmp = np.sum(np.abs(matrix_input -  np.matmul(np.matmul(V,           tridiag),              V.T) ))
                flag = tmp < 1e-3
                if(flag):
                    print("[Correct-tri][lanczos_git In = V@Tri@V*] {}".format( tmp))
                else:
                    print("[Error-tri][lanczos_git In = V@Tri@V*] {}".format( tmp))
                tmp = np.sum(np.abs(matrix_input -  np.matmul(np.matmul(H_cascade,   matrix_T),           H_cascade.T) ))
                flag = tmp < 1e-3
                if(flag):
                    print("[Correct-tri][lanczos tri In = V@tri@V*] {}".format( tmp))
                else:
                    print("[Error-tri][lanczos tri In = V@tri@V*] {}".format( tmp))
        print("[Check-tri][lanczos_git T = V*@In@V] {}".format(   np.sum(np.abs(tridiag      -  np.matmul(np.matmul(V.T,         matrix_input),         V) ))))
        print("[Check-tri][lanczos tri T = V_cof@In@V] {}".format(   np.sum(np.abs(matrix_T   -  np.matmul(np.matmul(H_cascade.T, matrix_input),      H_cascade) ))))
        matrix_A = np.copy(matrix_T)
        for j in range(m-1, -1, -1):
            print("j:",j)
            # for _ in range(3):
            ___ = -1
            while (np.matmul(matrix_A[j,0:j],matrix_A[j,0:j].T)>1e-12):
                ___ +=1
                print("___",___)
                s = matrix_A[j,j]
                I_j = np.diag(np.ones(j+1))
                A_shift = matrix_A[0:j+1, 0:j+1] - s*I_j

                safe_A_shift = np.copy(A_shift) if MUST_COPY_NO_CHANGE else A_shift
                Q_sophon,R_sophon = self.function_QR_HousHolder(safe_A_shift)
                # assert j!=30 ,Q_sophon[24]
                # self.PRINT_FUNC("j:{},_:{},Q:{}".format(j, _, Q_sophon))
                Q_sci, R_sci = scipy.linalg.qr(np.copy(safe_A_shift))
                assert np.sum(np.abs(Q_sophon-Q_sci))<1e-2
                assert np.sum(np.abs(R_sophon-R_sci))<1e-2
                Q = Q_sophon
                R = R_sophon
                assert Q.shape[0]==j+1, Q.shape[0]

                matrix_A[0:j+1, 0:j+1] = np.matmul(R,Q)+ s*I_j
                fake_X = np.zeros([m,m])
                fake_X[Q.shape[0]:,Q.shape[0]:] = np.eye(m-Q.shape[0])
                fake_X[0:Q.shape[0],0:Q.shape[0]] = Q
                X = np.matmul(X, fake_X)
        eig_values_scipy, eig_vectors_scipy = scipy.linalg.eigh(matrix_input)
        eig_values_scipy_tri, eig_vectors_scipy_tri = scipy.linalg.eigh(matrix_T)

        eignvalue_diag   = np.copy(matrix_A)
        eignvalue_asvector = eignvalue_diag.diagonal()
        eignvector      = np.copy(X)
        print("-------------[Print Necessary CMP Result for lanczos QR]------------------")
        if(m==n):
                print("[Check-tri][lanczos_git In = V@Tri@V*] {}".format( np.sum(np.abs(matrix_input -  np.matmul(np.matmul(V,           tridiag),              V.T) ))))
                print("[Check-tri][lanczos tri In = V@tri@V*] {}".format( np.sum(np.abs(matrix_input -  np.matmul(np.matmul(H_cascade,   matrix_T),           H_cascade.T) ))))
        print("[Check-tri][lanczos_git T = V*@In@V] {}".format(   np.sum(np.abs(tridiag      -  np.matmul(np.matmul(V.T,         matrix_input),         V) ))))
        print("[Check-tri][lanczos tri T = V*@In@V] {}".format(   np.sum(np.abs(matrix_T   -  np.matmul(np.matmul(H_cascade.T, matrix_input),      H_cascade) ))))
        print("[Check-QR][tri-diag tri=X@Diag@X.T] {}".format(np.sum(np.abs(matrix_T - np.matmul(np.matmul(X, eignvalue_diag), X.T)))))
        print("[Check-QR][tri-diag scipy tri=X@Diag@X.T] {}".format(np.sum(np.abs(matrix_T - np.matmul(np.matmul(eig_vectors_scipy_tri, np.diag(eig_values_scipy_tri)), eig_vectors_scipy_tri.T)))))
        eignvalue_diag_sortr =np.sort(eignvalue_diag.diagonal())
        if np.sum(np.abs(eig_values_scipy_tri-eignvalue_diag_sortr))>1e-3:
            print("[Warning] scipy QR is different from handy-QR for eignvalue!",eig_values_scipy_tri,eignvalue_diag_sortr)
        else:
            print("[Correct]eign_value is correct after sorted!")
        origin_eignvalue_asvector = eignvalue_asvector
        #NO H_cascade.transpose for lanczos as y = Vx
        origin_eignvector = np.matmul(H_cascade, eignvector)
        if(m==n):
            eig_values_scipy = np.diag(eig_values_scipy)
            print("[Check-QR][scipy   In =X'@Diag@X'.T] {}".format(np.sum(np.abs(matrix_input - np.matmul(np.matmul(eig_vectors_scipy, eig_values_scipy), eig_vectors_scipy.T)))))
            print("[Final-Check origin_sparse In =VXDiag(VX).T] {}".format(np.sum(np.abs(matrix_input - np.matmul(np.matmul(origin_eignvector, eignvalue_diag), origin_eignvector.T)))))
        self.check_if_column_orthogonal(origin_eignvector, "eignvector-lanczos")
        self.check_if_unitary(origin_eignvector, "eignvector-lanczos")
        print("-------------------------------------------------------------------------------")
        # for _, data in enumerate(H_cascade_inverse):
        #     print(data)
        # print("-------------------------------------------------------------------------------")
        # for _, data in enumerate(eignvector):
        #     print(data)
        # print("-------------------------------------------------------------------------------")
        # for _, data in enumerate(origin_eignvector):
        #     print(data)
        # print("-------------------------------------------------------------------------------")
        return origin_eignvalue_asvector,origin_eignvector

    def function_kmeans2_sophon_from_scipy(self, data, k, iter=10, thresh=1e-5, minit='random',
                missing='warn', check_finite=True, *, seed=None):
        data = np.copy(data)
        #[support] only support ++now
        nc = int(k)
        assert seed != None
        rng = np.random.RandomState(seed)
        #np  RandomState(MT19937)
        #cpp  <numpy.random._mt19937.MT19937 object at 0x13c6710>
        # rng = cpp_seed_mt19937(seed)
        code_book = self._kpp_sophon(data, k, rng)
        np.copy(data).astype('float32').tofile("./KNN_input_data.bin")
        np.copy(code_book).astype('float32').tofile("./KNN_weight.bin")
        for i in range(iter):
            # Compute the nearest neighbor for each obs using the current code book
            label = self.py_vq_sophon(np.copy(data), np.copy(code_book), check_finite=check_finite)[0]
            print("[sophon_data-label-{}]".format(i),np.sum(np.abs(label)))

            # Update the code book by computing centroids
            print("[sophon_data-update-data-{}]".format(i),np.sum(np.abs(data)))
            new_code_book, has_members = self.sophon_update_cluster_means(data, label, nc)
            print("[sophon_data-new_code_book-{}]".format(i),np.sum(np.abs(new_code_book)))
            if not has_members.all():
                print("[warning] code book update!")
                assert 0, "not support yet in backend"
                # Set the empty clusters to their previous positions
                new_code_book[~has_members] = code_book[~has_members]
            code_book = new_code_book
        return code_book, label

    def kmeans_sophon(self, data):
        k = data.shape[1]
        centroids, labels = scipy.cluster.vq.kmeans2(np.copy(data), k, minit='++', iter=2, seed=GLBOAL_UNIFIED_SEED)
        centroids_sophon, labels_sophon = self.function_kmeans2_sophon_from_scipy(np.copy(data), k, minit='++', iter=2, seed=GLBOAL_UNIFIED_SEED)
        np.copy(labels).astype('int32').tofile("./result_label.bin")
        np.copy(labels_sophon).astype('int32').tofile("./result_label_DQ.bin")
        if np.sum(np.abs(centroids_sophon - centroids)) < 1e-8:
            print("[ReproduceCMP scipy vs sophon] KNN centroids"  + '\x1b[6;30;42m' + ' Success!' + '\x1b[0m')
        else:
            print("[ReproduceCMP scipy vs sophon] KNN centroids failed")
        if np.sum(np.abs(labels - labels_sophon)) < 1e-8:
            print("[ReproduceCMP scipy vs sophon] KNN labels" + '\x1b[6;30;42m' + ' Success!' + '\x1b[0m')
        else:
            print("[ReproduceCMP scipy vs sophon] KNN labels failed")
            print("[Help] if fixed weight, cmp will naturally fail")
        # _, labels, _ = k_means(data, k,  random_state=None, n_init=20)
        # _, labels, _ = k_means(data, k,  random_state=None, n_init='auto')
        # _, labels, _ = k_means(data, k,  init='k-means++', random_state=None, n_init='auto', algorithm='elkan')
        # clustering = AffinityPropagation(random_state=5).fit(data)
        # labels = clustering.labels_
        return labels_sophon

    def run_reproducer(self, embeddings_input):
        embeddings = np.copy(embeddings_input)
        # Fallback for trivial cases
        if len(embeddings) <= 2:
            return [0] * len(embeddings)

        # Compute similarity matrix
        similarity_matrix = self.cosine_similarity(np.array(embeddings))
        # Prune matrix with p interval
        pruned_similarity_matrix = self.prune(similarity_matrix)
        # Compute Laplacian
        laplacian_matrix = self.laplacian(pruned_similarity_matrix)
        # Compute spectral embeddings
        self.check_Hermitian(laplacian_matrix)

        # spectral_embeddings = self.spectral_sophon(laplacian_matrix)
        spectral_embeddings = self.spectral(laplacian_matrix, self.num_spks, self.min_num_spks, self.max_num_spks)
        # Assign class labels
        labels = self.kmeans_sophon(spectral_embeddings)
        return labels

    def spectral_postprocess(self, eig_values, eig_vectors):
        num_spks = self.num_spks if self.num_spks is not None \
            else np.argmax(np.diff(eig_values[:self.max_num_spks + 1])) + 1
        print("num_spks lv1",num_spks)
        num_spks = max(num_spks, self.min_num_spks)
        print("num_spks lv2",num_spks)
        result = eig_vectors[:, :num_spks]
        return result,num_spks

    def spectral_compression(self, M):
        m = self.max_num_spks + 1
        M_m = M.shape[0]
        M =M[0:M_m,0:M_m]

        M_m = M.shape[0]
        eig_values_compressed_sophon, eig_vectors_compressed_sophon = self.function_lanczos(M[0:M_m,0:M_m], m  = m)

        eig_values, eig_vectors = scipy.linalg.eigh(M)
        eig_values_compressed, eig_vectors_compressed = scipy.sparse.linalg.eigsh(M, k = self.max_num_spks + 1,which="SM",v0=np.ones(M_m)/self.l2_norm(np.ones(M_m)))
        eig_values_compressed_sophon_sort=np.sort(eig_values_compressed_sophon)
        result_s0 ,num_spks_0 = self.spectral_postprocess(eig_values,                        eig_vectors)
        result_s1 ,num_spks_1 = self.spectral_postprocess(eig_values_compressed,             eig_vectors_compressed)
        result_s2 ,num_spks_2 = self.spectral_postprocess(eig_values_compressed_sophon_sort,      eig_vectors_compressed_sophon)
        assert num_spks_0==num_spks_1
        assert num_spks_2==num_spks_1

        index = np.argsort(eig_values_compressed_sophon)
        P = np.eye(index.shape[0])[index]
        assert np.sum(np.abs(P @ np.diag(eig_values_compressed_sophon) @ P.T - np.diag(eig_values_compressed_sophon_sort))) == 0.0
        # P^(-1)@P
        eig_vectors_compressed_sophon_by_sort = eig_vectors_compressed_sophon @ np.linalg.inv(P)

        labels_0 = self.kmeans(eig_vectors[:, :num_spks_0])
        labels_1 = self.kmeans(eig_vectors_compressed[:, :num_spks_1])
        assert eig_vectors_compressed_sophon_by_sort[:, :num_spks_2].shape == eig_vectors_compressed[:, :num_spks_1].shape
        labels_2 = self.kmeans(eig_vectors_compressed_sophon_by_sort[:, :num_spks_2])
        assert np.sum(np.abs(labels_0-labels_1))==0
        assert np.sum(np.abs(labels_1-labels_2))==0,(labels_1[0:30],labels_2[0:30])
        assert 0
        return

    def run_cmp(self, embeddings_input):
        embeddings = np.copy(embeddings_input)
        # Fallback for trivial cases
        if len(embeddings) <= 2:
            return [0] * len(embeddings)

        # Compute similarity matrix
        similarity_matrix = self.cosine_similarity(np.array(embeddings))
        # Prune matrix with p interval
        pruned_similarity_matrix = self.prune(similarity_matrix)
        # Compute Laplacian
        laplacian_matrix = self.laplacian(pruned_similarity_matrix)
        # Compute spectral embeddings
        self.check_Hermitian(laplacian_matrix)
        self.analysizer_sysmetric(laplacian_matrix)
        spectral_embeddings = self.spectral(laplacian_matrix, self.num_spks, self.min_num_spks, self.max_num_spks)
        # Assign class labels
        # np.copy(spectral_embeddings[:128,:]).astype('float32').tofile("./DQ_KNN_input.bin")

        spectral_embeddings=spectral_embeddings
        labels = self.kmeans(spectral_embeddings)
        labels2 = self.kmeans_sophon(spectral_embeddings)
        return labels2

    # # Define utility functions
    # def cosine_similarity(self, M):
    #     M = M / np.linalg.norm(M, axis=1, keepdims=True)
    #     return 0.5 * (1.0 + np.dot(M, M.T))

    # def prune(self, M):
    #     m = M.shape[0]
    #     if m < 1000:
    #         n = max(m - 10, 2)
    #     else:
    #         n = int((1.0 - self.p) * m)
    #     for i in range(m):
    #         indexes = np.argsort(M[i, :])
    #         low_indexes, high_indexes = indexes[0:n], indexes[n:m]
    #         M[i, low_indexes] = 0.0
    #         M[i, high_indexes] = 1.0
    #     return 0.5 * (M + M.T)

    # def laplacian(self, M):
    #     M[np.diag_indices(M.shape[0])] = 0.0
    #     D = np.diag(np.sum(np.abs(M), axis=1))
    #     return D - M
    # def kmeans(self,data):
    #         k = data.shape[1]
    #         data = data[:64,:64]
    #         centroids, labels = scipy.cluster.vq.kmeans2(np.copy(data), k, minit='++', iter=2, seed=GLBOAL_UNIFIED_SEED)
    #         # _, labels, _ = k_means(data, k,  random_state=None, n_init=20)
    #         # _, labels, _ = k_means(data, k,  random_state=None, n_init='auto')
    #         # _, labels, _ = k_means(data, k,  init='k-means++', random_state=None, n_init='auto', algorithm='elkan')
    #         # clustering = AffinityPropagation(random_state=5).fit(data)
    #         # labels = clustering.labels_
    #         return labels

    # def preprocess(self, path):
    #     input_cvte = np.loadtxt(path)
    #     time_step         = input_cvte[:, 0:2]
    #     matrix_embeddings = input_cvte[:, 2:]
    #     print("[matrix_embeddings]",matrix_embeddings.shape)
    #     return matrix_embeddings

    # def spectral(self, M, num_spks, min_num_spks, max_num_spks):
    #     np.copy(M).astype('float32').tofile("./ref_QR_input_M.bin")
    #     eig_values, eig_vectors = scipy.linalg.eigh(M)
    #     np.copy(eig_values).astype('float32').tofile("./ref_QR_output_eig_values.bin")
    #     np.copy(eig_vectors).astype('float32').tofile("./ref_QR_output_eig_vectors.bin")
    #     num_spks = num_spks if num_spks is not None \
    #         else np.argmax(np.diff(eig_values[:max_num_spks + 1])) + 1
    #     num_spks = max(num_spks, min_num_spks)
    #     return eig_vectors[:, :num_spks]

    # def run_origin(self, embeddings):
    #     # Fallback for trivial cases
    #     if len(embeddings) <= 2:
    #         return [0] * len(embeddings)

    #     # Compute similarity matrix
    #     similarity_matrix = self.cosine_similarity(np.array(embeddings))
    #     # Prune matrix with p interval
    #     pruned_similarity_matrix = self.prune(similarity_matrix)
    #     # Compute Laplacian
    #     laplacian_matrix = self.laplacian(pruned_similarity_matrix)
    #     # Compute spectral embeddings
    #     self.check_Hermitian(laplacian_matrix)

    #     spectral_embeddings = self.spectral(laplacian_matrix[:128,:128], self.num_spks, self.min_num_spks, self.max_num_spks)
    #     # Assign class labels
    #     labels = self.kmeans(spectral_embeddings)

    #     return labels


# fake_n = 128
# R_tpu_eignvalue_vector = np.fromfile("../nntoolchain/TPU1686/R_tpu_eignvalue_vector.dat",dtype=np.float32)
# R_tpu_eignvector = np.fromfile("../nntoolchain/TPU1686/R_tpu_eignvector.dat",            dtype=np.float32)
# R_tpu_eignvector = R_tpu_eignvector.reshape(fake_n, fake_n)
# R_tpu_eignvalue  = np.diag(R_tpu_eignvalue_vector)
# input_M          = np.fromfile("./DQ_QR_input_M.bin",dtype=np.float32).reshape(fake_n, fake_n)

# assert 0,np.sum(np.abs(input_M-np.matmul(np.matmul(R_tpu_eignvector, R_tpu_eignvalue),R_tpu_eignvector.T)))
# a = np.array(0.1491594911, dtype=np.float32)
# b = np.array(1.0, dtype=np.float32)
# a = np.array(25.0, dtype=np.float32)
# b = np.array(1.0, dtype=np.float32)

# c= b/np.sqrt(a, dtype=np.float32)
# assert c.dtype==np.float32,c.dtype
# def print_float_with_precision(num, precision):
#     format_string = "{:.%df}" % precision
#     print(format_string.format(num))

# precision = 10

# # Print float with specified precision
# print_float_with_precision(c, precision)
# assert 0
clusterOp =  Cluster_Reproductor(p=.01, num_spks=None, min_num_spks=2, max_num_spks=8)

# matrix_embeddings = clusterOp.preprocess("./dia_sample.txt")
matrix_embeddings = clusterOp.preprocess("./data/6k.txt")
matrix_embeddings = matrix_embeddings[0:600,:]
np.savetxt('DQ_input_M.txt',np.copy(matrix_embeddings[:128,:128]).astype('float32'))

# result_labels = clusterOp.run_origin(matrix_embeddings)
# result_labels = clusterOp.run_reproducer(matrix_embeddings[:128,:128])
result_labels = clusterOp.run_cmp(matrix_embeddings)
assert 0,result_labels

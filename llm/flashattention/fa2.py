import numpy as np

def flash_attention_v2_forward(Q, K, V, B_r=64, B_c=64):
    """
    FlashAttention-2前向传播实现
    参数：
    Q, K, V: 形状为(N, d)的输入矩阵
    B_r: Q的分块大小（行方向）
    B_c: K/V的分块大小（列方向）
    
    返回：
    O: 注意力输出矩阵 (N, d)
    L: logsumexp向量 (N,)
    """
    N, d = Q.shape
    assert K.shape == V.shape == (N, d), "输入维度不匹配"
    
    # 步骤1-2: 分块
    T_r = (N + B_r - 1) // B_r  # Q的分块数
    T_c = (N + B_c - 1) // B_c  # K/V的分块数
    
    # 初始化输出和logsumexp
    O = np.zeros((N, d), dtype=np.float32)
    L = np.zeros(N, dtype=np.float32)
    
    # 遍历每个Q块（外层循环）
    for i in range(T_r):
        # 步骤4: 加载Q_i（Python中直接切片）
        q_start = i * B_r
        q_end = min((i+1)*B_r, N)
        Q_i = Q[q_start:q_end]  # (Br, d)
        Br = Q_i.shape[0]
        
        # 步骤5: 初始化中间变量
        O_i = np.zeros((Br, d), dtype=np.float32)  # O_i^{(0)}
        l_i = np.zeros(Br, dtype=np.float32)       # ℓ_i^{(0)}
        m_i = np.full(Br, -np.inf, dtype=np.float32)  # m_i^{(0)}
        
        # 遍历每个K/V块（内层循环）
        for j in range(T_c):
            # 步骤7: 加载K_j, V_j
            k_start = j * B_c
            k_end = min((j+1)*B_c, N)
            K_j = K[k_start:k_end]  # (Bc, d)
            V_j = V[k_start:k_end]  # (Bc, d)
            Bc = K_j.shape[0]
            
            # 步骤8: 计算S_i^{(j)} = Q_i @ K_j^T
            S_ij = Q_i @ K_j.T  # (Br, Bc)
            
            # 步骤9: 更新最大值和中间变量
            # 计算当前块的行最大值
            m_ij = np.max(S_ij, axis=1)  # (Br,)
            # 更新全局最大值
            m_new = np.maximum(m_i, m_ij)
            
            # 计算指数化注意力权重（数值稳定）
            P_hat = np.exp(S_ij - m_new[:, None])  # (Br, Bc)
            
            # 更新累积sum_exp
            alpha_prev = np.exp(m_i - m_new)       # (Br,)
            l_ij = np.sum(P_hat, axis=1)           # (Br,)
            l_i_new = alpha_prev * l_i + l_ij
            
            # 步骤10: 更新输出块
            # 计算缩放因子并更新O_i
            O_i_scaled = alpha_prev[:, None] * O_i  # (Br, d)
            delta_O = P_hat @ V_j                   # (Br, d)
            O_i = O_i_scaled + delta_O
            
            # 保存更新后的中间变量
            l_i = l_i_new
            m_i = m_new
        
        # 步骤12: 归一化输出
        O_i_normalized = O_i / l_i[:, None]
        
        # 步骤13: 计算logsumexp
        L_i = m_i + np.log(l_i)
        
        # 步骤14-15: 写回结果
        O[q_start:q_end] = O_i_normalized
        L[q_start:q_end] = L_i
    
    return O, L

# 验证示例
if __name__ == "__main__":
    np.random.seed(42)
    N, d = 1024, 64
    Q = np.random.randn(N, d).astype(np.float32)
    K = np.random.randn(N, d).astype(np.float32)
    V = np.random.randn(N, d).astype(np.float32)
    
    # 标准Attention计算
    S = Q @ K.T
    P = np.exp(S - np.max(S, axis=1, keepdims=True))
    P /= np.sum(P, axis=1, keepdims=True)
    O_standard = P @ V
    L_standard = np.max(S, axis=1) + np.log(np.sum(np.exp(S - np.max(S, axis=1, keepdims=True)), axis=1))
    
    # FlashAttention计算
    O_flash, L_flash = flash_attention_v2_forward(Q, K, V, B_r=64, B_c=64)
    
    print("标准Attention输出:", O_standard)
    print("FlashAttention输出:", O_flash)
    
    # 验证误差
    print("输出最大绝对误差:", np.max(np.abs(O_flash - O_standard)))
    print("logsumexp最大绝对误差:", np.max(np.abs(L_flash - L_standard)))
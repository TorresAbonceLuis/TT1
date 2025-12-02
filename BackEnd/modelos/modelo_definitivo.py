import keras
from keras import layers, models, ops
import tensorflow as tf

# ========= PARÁMETROS =========
SEQ_LEN = 100
N_MELS = 229
N_KEYS = 88
CNN_FILTERS = [48, 48, 96] 
LSTM_UNITS = 256

def build_cnn_block(input_tensor, name_prefix):# Construye un bloque CNN para extracción de características
    # Reshape implícito para tratarlo como imagen (Batch, Time, Freq, 1)
    x = layers.Reshape((SEQ_LEN, N_MELS, 1), name=f"{name_prefix}_reshape")(input_tensor)
    for i, filters in enumerate(CNN_FILTERS):# Capas CNN
        x = layers.Conv2D(filters, (3, 3), padding='same', name=f"{name_prefix}_conv_{i+1}")(x)# Convolución 2D
        x = layers.BatchNormalization(name=f"{name_prefix}_bn_{i+1}")(x)# Normalización por batch
        x = layers.Activation('relu', name=f"{name_prefix}_relu_{i+1}")(x)# Activación ReLU
        # MaxPool en frecuencia (reducción progresiva)
        x = layers.MaxPooling2D((1, 2), name=f"{name_prefix}_pool_{i+1}")(x)# Pooling solo en dimensión de frecuencia
        x = layers.Dropout(0.25, name=f"{name_prefix}_dropout_{i+1}")(x)# Dropout para regularización

    # Aplanar
    current_shape = x.shape# Obtener forma actual
    features_aplanados = int(current_shape[2] * current_shape[3])# Calcular características aplanadas 
    x = layers.Reshape((SEQ_LEN, features_aplanados), name=f"{name_prefix}_flatten")(x)# Aplanar para LSTM
    return x

def build_transformer_block(x, num_heads=4, key_dim=64, name="attention"):
    # 1. Multi-Head Attention
    attn_out = layers.MultiHeadAttention(num_heads=num_heads, key_dim=key_dim, name=f"{name}_mha")(x, x)
    x = layers.Add(name=f"{name}_add")([x, attn_out])# Residual connection
    x = layers.LayerNormalization(name=f"{name}_norm")(x)# Normalización de capa
    return x

def build_modelo_definitivo(seq_len=SEQ_LEN, n_mels=N_MELS, n_keys=N_KEYS):
    inputs = layers.Input(shape=(seq_len, n_mels), name="input_spectrogram")
    # --- TORRE 1: ONSETS ---
    x_onsets = build_cnn_block(inputs, "Onsets")
    
    x_onsets = layers.Bidirectional(layers.LSTM(LSTM_UNITS, return_sequences=True), name="Onsets_BiLSTM")(x_onsets)
    x_onsets = layers.Dropout(0.5, name="Onsets_Drop")(x_onsets)
    # Salida Onsets
    output_onsets = layers.Dense(n_keys, activation='sigmoid', name="output_onsets")(x_onsets)
    # --- TORRE 2: FRAMES ---
    x_frames = build_cnn_block(inputs, "Frames")
    # Usamos una función auxiliar para output_shape
    def get_output_shape(input_shape):
        return input_shape

    # Detener gradiente CON output_shape explícito para evitar error al cargar
    onsets_detached = layers.Lambda(
        lambda x: tf.stop_gradient(x), 
        output_shape=get_output_shape,
        name="Stop_Gradient"
    )(output_onsets)
    
    x_bridge = layers.Concatenate(name="Bridge_Concat")([x_frames, onsets_detached])

    x_frames = layers.Bidirectional(layers.LSTM(LSTM_UNITS, return_sequences=True), name="Frames_BiLSTM")(x_bridge)
    x_frames = layers.Dropout(0.5, name="Frames_Drop")(x_frames)
    
    # --- ATENCIÓN ---
    x_frames = build_transformer_block(x_frames, name="Frames_Attn")

    # Salida Frames
    output_frames = layers.Dense(n_keys, activation='sigmoid', name="output_frames")(x_frames)

    # --- MODELO ---
    model = models.Model(inputs=inputs, outputs=[output_onsets, output_frames], name="Magenta_Definitivo")

    return model


if __name__ == "__main__":
    # Test de construcción del modelo
    print("="*60)
    print("🎹 TEST: Construcción del Modelo de Transcripción 🎹")
    print("="*60)
    
    model = build_modelo_definitivo()
    model.summary()
    
    print(f"\n✅ Modelo creado exitosamente")
    print(f"   - Secuencia: {SEQ_LEN} frames")
    print(f"   - Bandas Mel: {N_MELS}")
    print(f"   - Teclas: {N_KEYS}")
    print(f"   - Filtros CNN: {CNN_FILTERS}")
    print(f"   - LSTM Units: {LSTM_UNITS}")
    print(f"   - Parámetros: {model.count_params():,}")


if __name__ == "__main__":
    # Test de construcción del modelo
    print("="*60)
    print("🎹 TEST: Construcción del Modelo de Transcripción 🎹")
    print("="*60)
    
    model = build_modelo_definitivo()
    model.summary()
    
    print(f"\n✅ Modelo creado exitosamente")
    print(f"   - Secuencia: {SEQ_LEN} frames")
    print(f"   - Bandas Mel: {N_MELS}")
    print(f"   - Teclas: {N_KEYS}")
    print(f"   - Parámetros: {model.count_params():,}")

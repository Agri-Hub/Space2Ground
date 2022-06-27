import tensorflow_addons as tfa
import tensorflow.keras.backend as K
import tensorflow as tf

def doy_to_date(doy, year):
    return datetime.strptime(str(doy) + year, '%j%Y')
def get_band(df, band_name, with_id=False):
    bands = [x for x in df.columns if band_name in x]
    if with_id:
        bands = ["id"] + bands
    return df.loc[:, bands]

def simple_daily_interpolation(df, name, start_doy, end_doy, year='2021', interp_method='linear', ):
    n_cols = df.shape[1]

    df.index = df.index.astype(int)
    df.columns = [pd.to_datetime(x.split("_")[-1]) for x in df]

    date_of_doy = doy_to_date(end_doy, year)
    if df.columns[-1] < date_of_doy:
        df[date_of_doy] = np.nan
    dfT = df.T
    dfT = dfT.resample('1d').asfreq()

    df_daily = dfT.T.interpolate(interp_method, axis=1).ffill(axis=1).bfill(axis=1)
#     df_daily.columns = df_daily.columns.map(lambda t: "{}_{}".format(name, t.timetuple().tm_yday))
    df_daily = df_daily[df.columns]
    df_daily.columns = df_daily.columns.map(lambda t: "{}_mean_{}".format(name, t.date()))
    return df_daily


def daily_fs(fs, year, start_doy, end_doy, bandnames, s1 = False, s1_names = [], has_id=False, keep_init = True):
    band_list = []
#     print("Interpolation...")
    for b in tqdm(bandnames):
        band_df = get_band(fs, b)
        band_df = simple_daily_interpolation(band_df, b, start_doy, end_doy, year)
        cols = [x for x in band_df.columns if start_doy <= pd.to_datetime(x.split("_")[-1]).dayofyear <= end_doy]
        band_df = band_df[cols]
        band_list.append(band_df)

    if s1:
        band_list.append(fs.filter(regex = 'vv|vh'))
    fs_daily = pd.concat(band_list, axis=1, join='inner')
    if has_id:
        fs_daily.insert(0, 'id', fs["id"])
    return fs_daily

def attention_seq(query_value, scale):

    query, value = query_value
    score = tf.matmul(query, value, transpose_b=True) # (batch, timestamp, 1)
    score = scale*score # scale with a fixed number (it can be finetuned or learned during train)
    score = tf.nn.softmax(score, axis=1) # softmax on timestamp axis
    score = score*query # (batch, timestamp, feat)
    return score

def create_model(n_features=10, n_steps=7, n_units=32, n_steps_out=1, scale = 0.01,
                 n_classes = 2, layers = [128, 64], dropout = None, lr = 0.001):
    inp = tf.keras.layers.Input((n_steps, n_features))

    seq, state, _ = tf.keras.layers.LSTM(n_units, activation='relu', return_state=True, return_sequences=True)(inp)
    att = tf.keras.layers.Lambda(attention_seq, arguments={'scale': scale})([seq, tf.expand_dims(state,1)])
    x = tf.keras.layers.LSTM(n_units, activation='relu')(att)
    for l in layers:
        x = tf.keras.layers.Dense(l, activation='relu')(x)
        if dropout is None:
            continue
        else:
            x = tf.keras.layers.Dropout(dropout)(x)
    out = tf.keras.layers.Dense(n_classes, activation = 'softmax')(x)

    model = tf.keras.Model(inp, out)
    opt = tf.keras.optimizers.Adam(learning_rate=lr)
    model.compile(optimizer=opt, loss='binary_crossentropy', metrics=['categorical_accuracy'])
    return model

def model_train(X,y,Xval,yval,file_path,n_features = 10, n_steps = 7, batch_size=128, n_epochs=100, n_classes = 2, scale = 0.01,
                class_weights = None, layers = [128, 64], dropout = None, lr = 0.001):
    callback = tf.keras.callbacks.EarlyStopping(monitor = 'val_loss', min_delta =0, patience = 13)
#     log_dir = "logs/fit/" + "today"
#     tensorboard_callback = tf.keras.callbacks.TensorBoard(log_dir=log_dir, histogram_freq=1)

    
    checkpoint = tf.keras.callbacks.ModelCheckpoint(monitor = 'val_loss', filepath = file_path, save_best_only = True,verbose = 1)
#     tensorboard_clbk = tf.keras.callbacks.TensorBoard(log_dir='./', histogram_freq=1)
    reducer = tf.keras.callbacks.ReduceLROnPlateau(
                                    monitor='val_loss', factor=0.1, patience=7, verbose=1,
                                    mode='auto', min_delta=0.000001, cooldown=1, min_lr=0.0000099
                                )
    calls = [checkpoint,callback,reducer]
    model=create_model(n_features = n_features, n_units=128, n_steps=n_steps, n_steps_out=1, scale = scale, n_classes = n_classes,
                      layers = layers, dropout = dropout, lr = lr)
    model.fit(X,y,batch_size=batch_size,epochs=n_epochs,verbose=1, 
              callbacks = calls, validation_data=(Xval,yval), validation_batch_size = batch_size, 
              class_weight=class_weights)
    return model

def recall_m(y_true, y_pred):
    true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
    possible_positives = K.sum(K.round(K.clip(y_true, 0, 1)))
    recall = true_positives / (possible_positives + K.epsilon())
    return recall

def precision_m(y_true, y_pred):
    true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
    predicted_positives = K.sum(K.round(K.clip(y_pred, 0, 1)))
    precision = true_positives / (predicted_positives + K.epsilon())
    return precision

def f1_m(y_true, y_pred):
    precision = precision_m(y_true, y_pred)
    recall = recall_m(y_true, y_pred)
    return 2*((precision*recall)/(precision+recall+K.epsilon()))
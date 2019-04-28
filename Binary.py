class Classifier(object):
    def __init__(self, *classes):
        self.classes = classes
        self.vectorizer = None
        self.selector = None
        
    def create(self, layers, units, dropout_rate, input_shape, num_classes):
        model = keras.Sequential()
        model.add(keras.layers.Dropout(rate=dropout_rate, input_shape=input_shape))
        for _ in range(layers-1):
            model.add(keras.layers.Dense(units=units, activation=tf.nn.relu))
            model.add(keras.layers.Dropout(rate=dropout_rate))

        model.add(keras.layers.Dense(units=16, activation=tf.nn.relu))
        model.add(keras.layers.Dropout(rate=dropout_rate))
        model.add(keras.layers.Dense(units=num_classes, activation=tf.nn.sigmoid))
        return model
        
    def ngram_vectorize(self, **kwargs=None, train_texts=None, train_labels=None, val_texts=None, test_texts):
        # Method overloading
        if train_texts is None:
            x_test = self.vectorizer.transform(test_texts)
            x_test = self.selector.transform(x_test).astype('float32')
            return x_test
        else:
            vectorizer = TfidfVectorizer(kwargs)

            # Learn vocabulary from training texts and vectorize training texts.
            x_train = vectorizer.fit_transform(train_texts)
            self.vectorizer = vectorizer

            # Vectorize validation texts.
            x_val = vectorizer.transform(val_texts)
            
            # Vectorize test texts.
            x_test = self.vectorizer.transform(test_texts)

            # Select top 'k' of the vectorized features.
            selector = SelectKBest(f_classif, k=min(20000, x_train.shape[1]))
            selector.fit(x_train, train_labels)
            self.selector = selector
        
            x_train = selector.transform(x_train).astype('float32')
            x_val = selector.transform(x_val).astype('float32')
            x_test = self.selector.transform(x_test).astype('float32')
            return x_train, x_val, x_test
        
class BinaryClassifier(Classifier):
    def __init__(self):
        

    
class MultiClassifier(Classifier):
    def __init__(self):
        
    
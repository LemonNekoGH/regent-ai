from transformers import AutoModel
from transformers import AutoTokenizer


def download_text2vec_model():
    model_name = "shibing624/text2vec-base-multilingual"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name)

    tokenizer.save_pretrained("./models/" + model_name)
    model.save_pretrained("./models/" + model_name)


download_text2vec_model()

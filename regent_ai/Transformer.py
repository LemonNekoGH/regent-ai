import numpy as np

from sentence_transformers import SentenceTransformer

_model = SentenceTransformer('./models/shibing624/text2vec-base-multilingual')


def embeddings(sentence: str) -> np.ndarray:
    result = _model.encode(sentence, output_value=None)
    # token_usages = result["token_embeddings"].shape[0]

    # print({
    #     'input': sentence,
    #     "usage": {"prompt_tokens": token_usages, "total_tokens": token_usages},
    # })

    result_numpy = result["sentence_embedding"].cpu().detach().numpy()

    return result_numpy

from indexing.similarity import cosine_similarity, dot_product_sparse


def test_dot_product_sparse():
    a = {"x": 2.0, "y": 3.0}
    b = {"y": 10.0, "z": 5.0}
    assert dot_product_sparse(a, b) == 30.0


def test_cosine_similarity_zero_norm():
    assert cosine_similarity(1.0, 0.0, 2.0) == 0.0


def test_cosine_similarity_identity():
    assert cosine_similarity(2.0, 2.0, 1.0) == 1.0


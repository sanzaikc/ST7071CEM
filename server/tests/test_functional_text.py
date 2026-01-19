from indexing.text import l2_norm, term_frequencies, tf_weight, tokenize, vector_weights


def test_tokenize_basic():
    tokens = tokenize("Hello, world! It's 2026.")
    assert tokens == ["hello", "world", "it's", "2026"]


def test_tf_weight_monotonic():
    assert tf_weight(1) > 0
    assert tf_weight(2) > tf_weight(1)


def test_vector_weights_and_norm():
    tf = term_frequencies(["a", "a", "b"])
    weights = vector_weights(tf)
    assert set(weights.keys()) == {"a", "b"}
    assert weights["a"] > weights["b"]
    assert l2_norm(weights) > 0


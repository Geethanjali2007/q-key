from app.services.conditioning_service import condition_entropy, derive_key_material


def test_condition_entropy_produces_32_bytes():
    conditioned = condition_entropy(b"some raw entropy input")
    assert len(conditioned) == 32


def test_condition_entropy_is_deterministic_for_same_input():
    a = condition_entropy(b"fixed input")
    b = condition_entropy(b"fixed input")
    assert a == b


def test_derive_key_material_length():
    key = derive_key_material(b"raw entropy bytes here", length=32)
    assert len(key) == 32


def test_derive_key_material_different_inputs_differ():
    key_a = derive_key_material(b"input-a")
    key_b = derive_key_material(b"input-b")
    assert key_a != key_b

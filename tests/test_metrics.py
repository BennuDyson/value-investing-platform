from screens.metrics import graham_number, margin_of_safety, roe


def test_graham_number_calculation() -> None:
    result = graham_number(4.0, 25.0)
    assert result is not None
    assert round(result, 2) == 47.43


def test_roe_calculation() -> None:
    assert roe(30.0, 150.0) == 0.2


def test_margin_of_safety_logic() -> None:
    assert margin_of_safety(100.0, 70.0) == 0.3
    assert margin_of_safety(100.0, 110.0) == -0.1

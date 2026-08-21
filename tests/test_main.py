import main


def test_model_exists():
    assert main.MODEL is not None
    assert isinstance(main.MODEL, str)
    assert len(main.MODEL) > 0


def test_conversation_history_exists():
    assert hasattr(main, "conversation_history")
    assert isinstance(main.conversation_history, list)


def test_conversation_memory():
    main.conversation_history.clear()

    main.conversation_history.append({
        "role": "user",
        "content": "Hello"
    })

    assert len(main.conversation_history) == 1
    assert main.conversation_history[0]["role"] == "user"
    assert main.conversation_history[0]["content"] == "Hello"

    main.conversation_history.clear()


def test_gpu_stats():
    stats = main.get_gpu_stats()

    assert stats is not None
    assert isinstance(stats, tuple)
    assert len(stats) == 3


def test_speak_function_exists():
    assert callable(main.speak)


def test_listen_function_exists():
    assert callable(main.listen)


def test_normal_chat_function_exists():
    assert callable(main.normal_chat)


def test_document_chat_function_exists():
    assert callable(main.document_chat)


def test_voice_chat_function_exists():
    assert callable(main.voice_chat)
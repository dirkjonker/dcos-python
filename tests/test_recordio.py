import json

from dcos import recordio


def test_encode():
    encoder = recordio.Encoder(lambda s: json.dumps(s).encode("UTF-8"))

    message = {
        "type": "ATTACH_CONTAINER_OUTPUT",
        "containerId": "123456789"
    }

    encoded = encoder.encode(message)

    string = json.dumps(message)
    assert encoded == (str(len(string)) + "\n" + string).encode("UTF-8")


def test_encode_decode():
    total_messages = 10

    encoder = recordio.Encoder(lambda s: json.dumps(s).encode("UTF-8"))

    decoder = recordio.Decoder(lambda s: json.loads(s.decode("UTF-8")))

    message = {
        "type": "ATTACH_CONTAINER_OUTPUT",
        "containerId": "123456789"
    }

    encoded = b""
    for i in range(total_messages):
        encoded += encoder.encode(message)

    all_records = []
    offset = 0
    chunk_size = 5
    while offset < len(encoded):
        records = decoder.decode(encoded[offset:offset + chunk_size])
        print(records)
        all_records.extend(records)
        offset += chunk_size

    print(encoded)
    print(all_records)

    assert len(all_records) == total_messages

    for record in all_records:
        assert record == message

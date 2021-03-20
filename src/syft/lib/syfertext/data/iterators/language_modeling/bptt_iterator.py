# stdlib
from typing import List
from typing import Optional
from uuid import UUID

# third party
from google.protobuf.reflection import GeneratedProtocolMessageType
from syfertext.data.iterators.language_modeling import BPTTIterator
from syfertext.data.readers.language_modeling import TextReader
from syfertext.encoders.sentence_encoder import SentenceEncoder

# syft relative
from ......core.common import UID
from ......core.store.storeable_object import StorableObject
from ......generate_wrapper import GenerateWrapper
from ......proto.lib.syfertext.data.iterators.language_modeling.bptt_iterator_pb2 import BPTTIterator as BPTTIterator_PB
from ......proto.lib.syfertext.data.readers.language_modeling.text_reader_pb2 import TextReader as TextReader_PB
from ......proto.lib.syfertext.encoders.sentence_encoder_pb2 import SentenceEncoder as SentenceEncoder_PB
from ....tokenizers.spacy_tokenizer import object2proto as spacy_tokenizer2proto
from ....tokenizers.spacy_tokenizer import proto2object as proto2spacy_tokenizer
from ......util import aggressive_set_attr



def object2proto(obj: BPTTIterator) -> BPTTIterator_PB:

    # For convenience, rename the object.
    bptt_iterator = obj

    bptt_iterator_pb = BPTTIterator_PB()

    bptt_iterator_pb.uuid = bptt_iterator.id.value.bytes
    bptt_iterator_pb.batch_size = bptt_iterator.batch_size
    bptt_iterator_pb.bptt_len = bptt_iterator.bptt_len
    bptt_iterator_pb.shuffle = bptt_iterator.shuffle                
    bptt_iterator_pb.mode = bptt_iterator.mode

    # -------------------------------------
    # Create the TextReader protobuf object
    # -------------------------------------

    # Get the Dataset reader object
    text_reader = bptt_iterator.dataset_reader

    # Create/get its uuid
    bptt_iterator_pb.dataset_reader.uuid = getattr(text_reader, 'id', UID()).value.bytes

    bptt_iterator_pb.dataset_reader.mode = text_reader.mode

    # Get the sentence encoder object
    sentence_encoder = bptt_iterator.dataset_reader.encoder

    bptt_iterator_pb.dataset_reader.encoder.uuid = getattr(sentence_encoder, 'id', UID()).value.bytes

    # Populate the tokenizer protobuf part in the iterator protobuf
    spacy_tokenizer2proto(obj = sentence_encoder.tokenizer,
                          obj_pb = bptt_iterator_pb.dataset_reader.encoder.tokenizer
                          )

    return bptt_iterator_pb


def proto2object(proto: BPTTIterator_PB) -> BPTTIterator:

    # For convenience, rename the `proto` argument
    bptt_iterator_pb = proto

    # Extract the property values
    batch_size = bptt_iterator_pb.batch_size
    bptt_len = bptt_iterator_pb.bptt_len
    shuffle = bptt_iterator_pb.shuffle
    mode = bptt_iterator_pb.mode

    # ------------------------------------
    # Create the TextReader object
    # ------------------------------------

    # get the tokenizer object from the protobuf object
    tokenizer_pb =  bptt_iterator_pb.dataset_reader.encoder.tokenizer
    tokenizer = proto2spacy_tokenizer(proto = tokenizer_pb)

    uuid = UUID(bytes = tokenizer_pb.uuid)
    tokenizer.id = UID(value = uuid)

    # Create the sentence encoder object from its protobuf
    sentence_encoder_pb = bptt_iterator_pb.dataset_reader.encoder

    sentence_encoder = SentenceEncoder(tokenizer = tokenizer)

    uuid = UUID(bytes = sentence_encoder_pb.uuid)
    sentence_encoder.id = UID(value = uuid)


    # Now deal with the text reader
    text_reader_pb = bptt_iterator_pb.dataset_reader

    text_reader = TextReader(mode = text_reader_pb.mode,
                             encoder = sentence_encoder)


    uuid = UUID(bytes = text_reader_pb.uuid)
    text_reader.id = UID(value = uuid)


    # Finaly, create the BPTTIterator object
    bptt_iterator = BPTTIterator(batch_size = batch_size,
                                 bptt_len = bptt_len,
                                 shuffle = shuffle,
                                 mode = mode,
                                 dataset_reader = text_reader
                                 )


    uuid = UUID(bytes = bptt_iterator_pb.uuid)
    bptt_iterator.id = UID(value = uuid)

    return bptt_iterator

    
GenerateWrapper(
    wrapped_type=BPTTIterator,
    import_path="syfertext.data.iterators.BPTTIterator",
    protobuf_scheme=BPTTIterator_PB,
    type_object2proto=object2proto,
    type_proto2object=proto2object,
)

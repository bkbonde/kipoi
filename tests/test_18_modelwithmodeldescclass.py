import numpy as np
import pandas as pd

import kipoi
from kipoi_utils.utils import cd

def test_model():
    example_dir = "example/models/mdcexample"
    model = kipoi.get_model(example_dir, source="dir")
    # model = kipoi.get_model("APARENT/site_probabilities", source="kipoi")

def test_model_predict_example():
    example_dir = "example/models/mdcexample"
    model = kipoi.get_model(example_dir, source="dir")
    # model = kipoi.get_model("APARENT/site_probabilities", source="kipoi")
    pred = model.pipeline.predict_example(batch_size=32)


def test_model_predict():
    example_dir = "example/models/mdcexample"
    model = kipoi.get_model(example_dir, source="dir")
    # model = kipoi.get_model("APARENT/site_probabilities", source="kipoi")
    dl_kwargs = model.default_dataloader.example_kwargs
    with cd(model.source_dir):
        ret = model.pipeline.predict(dl_kwargs)
    assert isinstance(ret, dict)
    assert list(ret.keys()) == ["distal_prop", "site_props"]
    assert isinstance(ret["distal_prop"], np.ndarray)
    assert isinstance(ret["site_props"], np.ndarray)
    assert ret["distal_prop"].shape == (618, )
    assert ret["site_props"].shape == (618, 205)

def test_predict_to_file(tmpdir):
    h5_tmpfile = str(tmpdir.mkdir("example").join("out.h5"))
    example_dir = "example/models/mdcexample"
    model = kipoi.get_model(example_dir, source="dir")
    dl_kwargs = model.default_dataloader.example_kwargs
    with cd(model.source_dir):
        model.pipeline.predict_to_file(h5_tmpfile, dl_kwargs)
    preds = kipoi.readers.HDF5Reader.load(h5_tmpfile)
    assert 'preds' in preds

def test_predict_to_file_with_metadata_hdf5(tmpdir):
    h5_tmpfile = str(tmpdir.mkdir("example").join("out.h5"))
    example_dir = "example/models/mdcexample"
    model = kipoi.get_model(example_dir, source="dir")
    dl_kwargs = model.default_dataloader.example_kwargs
    with cd(model.source_dir):
        model.pipeline.predict_to_file(h5_tmpfile, dl_kwargs,keep_metadata=True)
    preds_and_metadata = kipoi.readers.HDF5Reader.load(h5_tmpfile)
    assert 'preds' in preds_and_metadata
    assert 'metadata' in preds_and_metadata
    assert len(preds_and_metadata['metadata']['ranges']['chr']) == 618
    assert len(preds_and_metadata['preds']['distal_prop']) == 618
    assert len(preds_and_metadata['preds']['site_props']) == 618

def test_predict_to_file_with_metadata_tsv(tmpdir):
    tsv_tmpfile_metadata = str(tmpdir.mkdir("example").join("out_with_metadata.tsv"))
    example_dir = "example/models/mdcexample"
    model = kipoi.get_model(example_dir, source="dir")
    dl_kwargs = model.default_dataloader.example_kwargs
    with cd(model.source_dir):
        model.pipeline.predict_to_file(tsv_tmpfile_metadata, dl_kwargs,keep_metadata=True)
    preds_and_metadata = pd.read_csv(tsv_tmpfile_metadata, sep='\t')
    assert 'metadata/ranges/chr' in preds_and_metadata.columns 
    assert 'preds/distal_prop/100' in preds_and_metadata.columns
    assert len(preds_and_metadata['metadata/ranges/chr']) == 618
    assert len(preds_and_metadata['preds/distal_prop/100']) == 618
    assert preds_and_metadata.at[0,'preds/distal_prop/100'] == pytest.approx(0.4168229, rel=1e-05)


def test_predict_to_file_without_metadata_tsv(tmpdir):
    tsv_tmpfile = str(tmpdir.mkdir("example").join("out.tsv"))
    model = kipoi.get_model("Basset", source="kipoi")
    dl_kwargs = model.default_dataloader.example_kwargs
    with cd(model.source_dir):
        model.pipeline.predict_to_file(tsv_tmpfile, dl_kwargs)
    preds = pd.read_csv(tsv_tmpfile, sep='\t')
    assert 'metadata/ranges/chr' not in preds.columns 
    assert 'preds/100' in preds.columns
    assert preds.at[0,'preds/100'] == pytest.approx(0.4168229, rel=1e-05)

---
layout: page
title: Word Vectors
keywords: stanza, model training, embedding
permalink: '/word_vectors.html'
nav_order: 6
parent: Usage
---

## Downloading Word Vectors

To replicate the system performance on the CoNLL 2018 shared task, we have prepared a script for you to download all word vector files. Simply run from the source directory:
```bash
bash scripts/download_vectors.sh ${wordvec_dir}
```
where `${wordvec_dir}` is the target directory to store the word vector files, and should be the same as where the environment variable `WORDVEC_DIR` is pointed to.

The above script will first download the pretrained word2vec embeddings released from the CoNLL 2017 Shared Task, which can be found [here](https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-1989/word-embeddings-conll17.tar?sequence=9&isAllowed=y). For languages not in this list, it will download the [FastText embeddings](https://fasttext.cc/docs/en/crawl-vectors.html) from Facebook. Note that the total size of all downloaded vector files will be ~30G, therefore please use this script with caution.

After running the script, your embedding vector files will be organized in the following way:
`${WORDVEC_DIR}/{language}/{language_code}.vectors.xz`. For example, the word2vec file for English should be put into `$WORDVEC_DIR/English/en.vectors.xz`. If you use your own vector files, please make sure you arrange them in a similar fashion as described above.

{% include alerts.html %}
{{ note }}
{{ "If you only want one language's word vectors, you can get them from your [STANZA_RESOURCES](download_models.md) directory.  For example, word vectors used for English go to `~stanza_resources/en/pretrain/ewt.pt` by default" | markdownify }}
{{ end }}


## Using alternate word vectors

The simplest way to retrain models for an existing language with new data is to use the existing word vectors.  Generally we redistribute word vectors built with word2vec or fasttext.

If you retrain the models with new word vectors, you will need to provide the path for those word vectors when creating a pipeline.  Otherwise, the pipeline will try to use the default word vectors for that language and/or package.  To specify a different set of word vectors, you can supply the following arguments as relevant:

```
pos_pretrain_path
depparse_pretrain_path
sentiment_pretrain_path
```

This is in addition to specifying the path for the model you have retrained.  Therefore, the complete arguments for initializing a pipeline with a new POS model trained with new word vectors will look like this:

```python
pipe = stanza.Pipeline(lang="en", processors="tokenize,pos", pos_pretrain_path="new_en_wv.pt", pos_model_path="new_pos_model.pt")
```

Currently the NER model includes the word vectors in the finished model, so no such argument is necessary, although that may change in the future.

The pretrain embedding file expected by the pipeline is the `.pt` format Torch uses to save models.  The module which loads embeddings will convert a text file to a `.pt` file if needed, so you can use the following code snippet to create the `.pt` file:

```
from stanza.models.common.pretrain import Pretrain
pt = Pretrain("foo.pt", "new_vectors.txt")
pt.load()
```


## Included utilities

In general we convert the embeddings into a torch module for faster
loading and smaller disk sizes.  A script is provided which does that:

```
python3 stanza/models/common/convert_pretrain.py ~/stanza/saved_models/pos/fo_fasttext.pretrain.pt ~/extern_data/wordvec/fasttext/faroese.txt -1
```

The third argument sets the limit on how many vectors to keep.

Coming Soon in v1.3
{: .label .label-green }

There is also a script for counting how many times words in a UD training set appear in an embedding:

```
stanza/models/common/count_pretrain_coverage.py
```
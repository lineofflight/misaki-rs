# Misaki-RS

[![Crates.io](https://img.shields.io/crates/v/misaki-rs)](https://crates.io/crates/misaki-rs)


**misaki-rs** is a self-contained, high-performance Rust port of the [Misaki](https://github.com/hexgrad/misaki) G2P (Grapheme-to-Phoneme) engine. 

It is specifically designed for use with TTS models like **Kokoro**, providing accurate Part-of-Speech aware phonemization for English text.

## Features

- **Self-Contained**: All lexicons, dictionaries, and Part-of-Speech tagger weights are embedded directly into the binary at compile time. No external resource files are required at runtime.
- **POS-Aware Phonemization**: Uses an averaged perceptron tagger to handle heteronyms (words with different pronunciations based on context, e.g., *object* as a noun vs. verb).
- **Multi-Dialect Support**: Supports both **US English** (en-us) and **British English** (en-gb).
- **Morphological Stemming**: Intelligent handling of suffixes (plurals, past tense, continuous tense). Other rules may be added in the future. Currently those are:
    -  s plural stemming
    - ed past tense stemming
    - ing continuous tense stemming
- **Number Conversion**: Automatically converts numeric values into their spoken word equivalents.
- **Optional espeak fallback** (feature `espeak`, enabled by default): For out-of-vocabulary words, use [espeak-ng](https://github.com/espeak-ng/espeak-ng) to produce phonemes. Disable with `default-features = false` for a smaller build with no system espeak dependency; unknown words will then be spelled letter-by-letter or marked as unknown.


## Why “spelling out” when espeak is disabled?

When a word is not in the lexicon and no rule applies, the engine needs a fallback. With the `espeak` feature **enabled**, that fallback is espeak-ng: the word is sent to espeak and its IPA output is converted to the engine’s phoneme set. With the `espeak` feature **disabled**, there is no external fallback, so the engine falls back to **character-by-character spelling**: each letter is phonemized as its name (e.g. “B” → “bˈi”, “K” → “kˈe‍ɪ”). So for example “eBook” becomes the sequence of letter names (E, B, O, O, K) instead of the word “e-book”. Single-character tokens and unrecognized characters may be marked as unknown (❓) instead. This behavior is intentional so that builds without espeak still produce some output rather than failing.


## Testing espeak

To check that espeak fallback is working, phonemize an out-of-vocabulary word like `"eBook"` and assert it does not contain the unknown marker and is not spelled letter-by-letter:

```bash
cargo test test_ebook_with_espeak -- --nocapture
```

You should see output like `eBook (with espeak): ˈi bˈʊk.` (word-like). Without the espeak feature, the same word is spelled out: `cargo test test_ebook_without_espeak --no-default-features -- --nocapture` gives e.g. `eBook (without espeak): ˈi  bˈi  ˈo‍ʊ  ˈo‍ʊ  kˈe‍ɪ` (E, B, O, O, K as letter names).


## Installation

Add this to your `Cargo.toml`:

```toml
[dependencies]
misaki-rs = "0.6.0"
```

**Optional: disable espeak fallback** (smaller build, no espeak-ng dependency):

```toml
[dependencies]
misaki-rs = { version = "0.6.0", default-features = false }
```

To depend on misaki-rs without default features but still use espeak:

```toml
misaki-rs = { version = "0.6.0", default-features = false, features = ["espeak"] }
```

## Quick Start

```rust
use misaki_rs::G2P;

fn main() {
    // Initialize for US English (false = US, true = GB)
    let g2p = G2P::new(false); 
    
    let (phonemes, tokens) = g2p.g2p("Hello, world! 123");
    println!("US Phonemes: {}", phonemes);
    
    // Initialize for British English
    let g2p_gb = G2P::new(true);
    let (phonemes_gb, _) = g2p_gb.g2p("The schedule is full.");
    println!("GB Phonemes: {}", phonemes_gb);
}
```

## Custom OOV fallback

If you want to override the default out-of-vocabulary behavior, inject your own fallback implementation by implementing the `Fallback` trait and passing it to `G2P::with_fallback`.

```rust
use misaki_rs::{Fallback, FallbackError, G2P, Language};

struct CustomFallback;

impl Fallback for CustomFallback {
    fn phonemize(&self, word: &str) -> Result<String, FallbackError> {
        // Replace this with your own phoneme generation logic.
        Ok(format!("custom:{word}"))
    }
}

fn main() {
    let g2p = G2P::with_fallback(Language::EnglishUS, Some(Box::new(CustomFallback)));
    let (phonemes, _) = g2p.g2p("qzxwv");
    println!("{}", phonemes);
}
```

This is useful when you want a custom pronunciation source, a dictionary lookup, or a second-pass rule engine for unknown words instead of the built-in `espeak` fallback.

## Pronunciations

The dictionaries in `data/` are a hybrid of two sources:

- Every word [hexgrad/misaki](https://github.com/hexgrad/misaki) has, about 197,000 British and 184,000 American, takes misaki's entry and tier, gold or silver, as at commit `e820629`. A word said differently by part of speech, such as *present* or *separate*, keeps a reading for each. Only the notation changes: misaki's one-letter diphthongs and affricates (`A`, `I`, `O`, `Q`, `W`, `Y`, `ʤ`, `ʧ`) are written as pairs joined by U+200D (`e‍ɪ`, `a‍ɪ`, `o‍ʊ`, `ə‍ʊ`, `a‍ʊ`, `ɔ‍ɪ`, `d‍ʒ`, `t‍ʃ`).
- Every word misaki lacks, about 194,000 British and 206,000 American, keeps the entry `expand_dicts.py` generated for it with eSpeak-ng.

`scripts/build_hybrid_dictionary.py` builds `data/` again from both.

## Scope

This repository aims to provide a lightweight and efficient alternative to ONNX-based phonemizers for Rust applications. It eliminates the need for external C++ dependencies or large model files by porting the logic and data into native Rust.

## License

This project is based on the original Misaki library. The entries in `data/` for words misaki has come from [hexgrad/misaki](https://github.com/hexgrad/misaki) under the [Apache License 2.0](https://github.com/hexgrad/misaki/blob/main/LICENSE), changed only in notation as described under Pronunciations. The entries for words it lacks were generated with eSpeak-ng.

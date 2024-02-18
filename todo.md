----The I HAVE NO IDEA WHAT I'M DOING Edition~~
Work on making docx_handler work, need to be able to use docx files as input - Likely just gonna pull the images out, replace with text and put back in later, would need to adjust prompt building to account for this.

The thing is, I don't really see a way to do this. We'd extract the text, but since we're translating it, we'd have to put it back in the same place, and I don't see how that's possible cause of structure changes. 

"Is there a way to add a feature that highlights names/words that are not indexed in the replacement file during preprocessing
Since there are sometimes new names or phrases in new volumes, being able to identify them before hand would be ideal so we don’t just come across them randomly during the editing process" - cast

Could be possible, I'd have to add it to Kairyou though, we can ner the entire text, scan for all words that are flagged as names or pronouns, and then compare that to the replacement file. If it's not in the replacement file, we can flag it. Flagging could be weird though, we can either note down index and word, or we can do a word marker, but we'd have to do it in a way that gpt doesn't mess with it.
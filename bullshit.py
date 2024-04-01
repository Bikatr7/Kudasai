from easytl import EasyTL

async def main():

    EasyTL.set_api_key("gemini", "AIzaSyAKKLwwemQ0sg9Wug79COk3kA2ehWGeO6o")
    EasyTL.set_api_key("deepl", "e319d8e3-dc1a-130a-1e07-b3df599accc2:fx")

    print("Api keys set")

    print(EasyTL.gemini_translate("私はかたわですよ", translation_instructions="Translate this to spanish"))
    print(EasyTL.gemini_translate(["私はかたわですよ","それは"], translation_instructions="Translate this to spanish"))

    print("phase 1 done, gemini sync test")

    print(await EasyTL.gemini_translate_async("私はかたわですよ", translation_instructions="Translate this to spanish"))
    print(await EasyTL.gemini_translate_async(["私はかたわですよ","それは"], translation_instructions="Translate this to spanish"))

    print("phase 2 done, gemini async test")

    print(EasyTL.deepl_translate("私はかたわですよ", target_lang="es"))
    print(EasyTL.deepl_translate(["私はかたわですよ","それは"], target_lang="es"))

    print("phase 3 done, deepl sync test")

    print(await EasyTL.deepl_translate_async("私はかたわですよ", target_lang="es"))
    print(await EasyTL.deepl_translate_async(["私はかたわですよ","それは"], target_lang="es"))

    print("phase 4 done, deepl async test")

if(__name__ == '__main__'):
    import asyncio
    asyncio.run(main())

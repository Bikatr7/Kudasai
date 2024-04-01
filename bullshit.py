from easytl import EasyTL

async def main():

    gemini_api_key = input("Enter gemini api key: ")
    deepl_api_key = input("Enter deepl api key: ")

    EasyTL.set_api_key("gemini", gemini_api_key)
    EasyTL.set_api_key("deepl", deepl_api_key)

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

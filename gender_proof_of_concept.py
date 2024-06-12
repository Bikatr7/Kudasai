sample = """
まさに２学期終了寸前,ギリギリのタイミングってことだな.
それでも,テストまではもう３週間と時間が残されていない.
学力の高い生徒たちは普段から勉強に対する姿勢が異なるため準備に要する時間は最低限でも構わないが,勝利のカギを握っているのは学力が平均以下の生徒たち.
"ＯＡＡでお互いのクラスの学力を見て,現状どうなっているか調べてみたの.私たちＢクラスの方が学力ＤやＥに相当する生徒が多い分だけ必然,得点の最大値は上回っている.つまり理想通りの戦いが出来れば１００%勝てるということでもあるわ"
ＯＡＡの学力が低い生徒を多く抱えているクラスの方が多く点数を取れる以上,Ａクラスの生徒たちがどんなに頑張っても獲得できる得点には限界がある.
こちらは相手が獲得できる最大得点を１点でも上回る計算で望めば勝てるわけだ.
と,まあこれは机上の空論もいいところ.あくまでも紙のように薄い確率の話だ.
40人近い生徒が参加する以上,満点を取ることは不可能に近い.Chabashira-senseiの口ぶりや特別試験のルールを加味しても難度の高い問題の割合はけして低くないと予想できる.
学力ＥやＤの生徒が容易に解ける問題なら,むしろそれこそバランスが取れない.
学力の高いクラス程不利な,理不尽な特別試験になってしまう.
勉強会のような集まりは必然だが,それだけで勝ちに導けるかは怪しいところだ.
"誰がどの程度の問題を解いて,そして次の相手にバトンを繋げるかも重要だよね"
落ち着いた口調のYōsukeが,Horikita Suzuneに確認をするようにそう問いかけた.
"ええ.シンプルに考えるのなら学力の低い生徒たちを率先して前に持っていき,自分たちが解けるだけ問題を解いてもらうのが分かりやすいけれど..."
制限時間は10分.問題を読み込む力も,生徒たちの力量で大きく変わって来る.
いきなり１００問もあるテスト問題から簡単な問題を探し出すだけでも一苦労だろう.
もし学力の高い生徒が高難度の問題を先に潰せば,それだけ学力の低い生徒は適切な問題を見つけ出すのに時間も要さない上に,落ち着いてその問題に集中することが出来る.
誰がどんな問題を解けて,解けないのか.
それを把握したうえで,指揮を執っていくような戦略もまた勝ちを拾う道筋だ.
これ以外にも方法は幾つかあるだろう.結局のところどの戦略を取るかを早い段階で固め,それに向けてクラスが動き出すことが重要だ.
"Chabashira-senseiは勝てる可能性があるって言ってたけど...不利は不利だよね"
"手堅く点数を重ねられたら,多分勝てないよな.相手はあのＡクラスだし"
クラスメイトたちの間ではそんな声も出始める.
これまで純粋な筆記試験の総合得点でＡクラスは一度も他のクラスを下回ったことがない.特異なルール込みでも強敵であることは変わらないだろう.
"今回はＡクラスとの対決だけれれど,実際には自分たちとの戦いよ.相手がどんな戦略を考えようとも私たちには関係ない.Sakayanagi-sanが相手だからと特別気負う必要はない"
表情の固い相手に,向き合うべきは外ではなく内側であることを強調する.
"作戦は私が可能な限り考える.その間,あなたたちには１秒でも多くの勉強をお願いしたいの"
これまで,いやもっと正確に言えば数週間前まで,生徒たちは期末テストの勉強に勤しんでいた.学生の本分が勉強とは言え,短期間で再び勉強となれば嫌気がさすもの.
それでも不満らしい不満を口にする生徒は１人も見当たらない.
"僕たちも可能な限りバックアップするよ"
"""

from modules.common.gender_util import GenderUtil

names_with_positions = GenderUtil.find_english_words(sample)

potential_names_with_positions = [(name, pos) for name, pos in names_with_positions if GenderUtil.is_potential_name(name)]

grouped_names = GenderUtil.group_names(sample, potential_names_with_positions)

actual_names = GenderUtil.discard_non_names(grouped_names)

print("-----------------")
print("'Names'")
print("-----------------")
print([name for name, _ in names_with_positions])

print("-----------------")
print("Potential 'names'")
print("-----------------")
print([name for name, _ in potential_names_with_positions])

print("-----------------")
print("Grouped 'names'")
print("-----------------")
print(grouped_names)

print("-----------------")
print("Actual names")
print("-----------------")
print(actual_names)


print("-----------------")
print("Gender prediction")
print("-----------------")

for name in actual_names:
    print(name, GenderUtil.find_name_gender(name, is_cote=True))

print("-----------------")
print("Determined Gender")
print("-----------------")

result = ""

for name in actual_names:
    gender = GenderUtil.find_name_gender(name, is_cote=True)
    if(gender and len(set(gender)) == 1 and "Unknown" not in gender):
        print(name, gender[0])
        result += f"{name} : {gender[0]}\n"
    else:
        result += f"{name} : Unknown\n"

with open("result.txt", "w", encoding="utf-8") as f:
    f.write(result)
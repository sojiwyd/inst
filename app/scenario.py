from dataclasses import dataclass


@dataclass(frozen=True)
class ScenarioStep:
    key: str
    text: str


SCENARIO_STEPS = [
    ScenarioStep(
        key="step_1",
        text=(
            "Привет 👀\n"
            "Ты написал “1864” — значит тебе зашёл этот проект\n\n"
            "Это на самом деле одно из самых странных и недооценённых мест у Кремля"
        ),
    ),
    ScenarioStep(
        key="step_2",
        text=(
            "Если коротко — это не новый ЖК\n\n"
            "Это бывшее Кокоревское подворье 1864 года\n\n"
            "В 19 веке там был целый мини-город:\n"
            "гостиница, магазины, банк\n\n"
            "Там жили Толстой, Чайковский, Репин\n\n"
            "Сейчас это всё превратили в закрытые резиденции"
        ),
    ),
    ScenarioStep(
        key="step_3",
        text=(
            "Самое дикое — локация\n\n"
            "Он прямо напротив Кремля, через реку\n\n"
            "И с некоторых окон ощущение,\n"
            "будто Спасская башня — это часть дома\n\n"
            "До Красной площади реально 5 минут пешком"
        ),
    ),
    ScenarioStep(
        key="step_4",
        text=(
            "Внутри ощущение не как в новостройке\n\n"
            "– мрамор\n"
            "– дерево\n"
            "– потолки до 7 метров\n"
            "– где-то оставили кирпич 1860-х\n\n"
            "Такое чувство, будто живёшь в истории, но с современным комфортом"
        ),
    ),
    ScenarioStep(
        key="step_5",
        text=(
            "Там всего около 60 апартаментов\n\n"
            "Площади — от 100 до почти 2000 квадратов\n\n"
            "Есть даже вилла внутри комплекса\n\n"
            "И свой SPA на несколько тысяч метров"
        ),
    ),
    ScenarioStep(
        key="step_6",
        text=(
            "Меня больше всего зацепило, что\n"
            "это буквально дом “перед Кремлём”\n\n"
            "Таких локаций в Москве больше нет"
        ),
    ),
]

RESET_WORDS = {"стоп", "stop", "/start", "сначала", "заново", "1864"}
TRIGGER_WORDS = {"1864"}


def first_step() -> ScenarioStep:
    return SCENARIO_STEPS[0]



def next_step(current_index: int | None) -> ScenarioStep | None:
    if current_index is None:
        return first_step()
    candidate = current_index + 1
    if candidate >= len(SCENARIO_STEPS):
        return None
    return SCENARIO_STEPS[candidate]

import random
from random import shuffle

from django.utils.text import slugify
from hypothesis import given, example, strategies as st, assume

from hypothesis.extra.django import TestCase


from gather_vision.apps.transport import models as transport_models
from gather_vision.apps.transport.models import event_cat_options
from gather_vision.obtain.core.data import GatherDataContainerCheck

# from hypothesis.extra import ghostwriter
# output = ghostwriter.magic(transport_models.Event.guess_category)

C_TRAIN_TRACK = transport_models.Event.CATEGORY_TRAIN_TRACK
C_TRAIN_STATION = transport_models.Event.CATEGORY_TRAIN_STATION
C_BUS_STOP = transport_models.Event.CATEGORY_BUS_STOP
C_TRAIN_SERVICE = transport_models.Event.CATEGORY_TRAIN_SERVICE
C_BUS_SERVICE = transport_models.Event.CATEGORY_BUS_SERVICE
C_FERRY_SERVICE = transport_models.Event.CATEGORY_FERRY_SERVICE
C_TRAIN_CARPARK = transport_models.Event.CATEGORY_TRAIN_CARPARK


@st.composite
def event_category_examples(draw):
    raw: str = draw(st.text())
    random_option_order: list[GatherDataContainerCheck] = list(
        random.sample(event_cat_options, len(event_cat_options))
    )
    for opt in random_option_order:
        value = slugify(raw or "").split("-")
        if opt.check(value):
            return raw, opt.label


class TransportEventCategoryTests(TestCase):
    @given(data=event_category_examples())
    @example(data=(None, None))
    @example(data=("", None))

    # CATEGORY_TRAIN_TRACK
    @example(
        data=(
            "lines; track; ELLIPSIS; Airport Line; Beenleigh Line; Cleveland Line",
            C_TRAIN_TRACK,
        ),
    )
    @example(
        data=(
            "lines; track; ELLIPSIS; Airport Line; Beenleigh Line; Gold Coast Line",
            C_TRAIN_TRACK,
        ),
    )
    @example(
        data=(
            "lines; track; ELLIPSIS; Beenleigh Line; Caboolture Line; Cleveland Line",
            C_TRAIN_TRACK,
        ),
    )
    @example(data=("line; track; Shorncliffe Line", C_TRAIN_TRACK))
    @example(data=("line; track; Redcliffe Peninsula Line", C_TRAIN_TRACK))
    @example(
        data=(
            "lines; track; ELLIPSIS; Caboolture Line; Redcliffe Peninsula Line",
            C_TRAIN_TRACK,
        ),
    )
    @example(
        data=(
            "line; track; ELLIPSIS; Caboolture Line; Redcliffe Peninsula Line",
            C_TRAIN_TRACK,
        ),
    )
    @example(
        data=("lines; track; Ipswich/Rosewood Line; Springfield Line", C_TRAIN_TRACK),
    )
    @example(
        data=("lines; track; Ipswich/Rosewood Line; Springfield Line", C_TRAIN_TRACK),
    )
    @example(data=("line; track; Shorncliffe Line", C_TRAIN_TRACK))
    @example(
        data=(
            "line; track; ELLIPSIS; Caboolture Line; Redcliffe Peninsula Line",
            C_TRAIN_TRACK,
        ),
    )
    @example(
        data=("lines; track; Ipswich/Rosewood Line; Springfield Line", C_TRAIN_TRACK),
    )

    # CATEGORY_TRAIN_STATION
    @example(data=("station; 109; Beenleigh Line", C_TRAIN_STATION))
    @example(data=("station; Beenleigh Line", C_TRAIN_STATION))
    @example(data=("station; Beenleigh Line", C_TRAIN_STATION))
    @example(
        data=(
            "entrance; station; ELLIPSIS; Airport Line; Beenleigh Line; Caboolture Line",
            C_TRAIN_STATION,
        ),
    )
    @example(
        data=(
            "station; 104; 105; 109; ELLIPSIS; Beenleigh Line; Ferny Grove Line",
            C_TRAIN_STATION,
        ),
    )
    @example(
        data=(
            "platforms; station; ELLIPSIS; Airport Line; Beenleigh Line; Caboolture Line",
            C_TRAIN_STATION,
        ),
    )
    @example(
        data=(
            "entrance; station; 111; 222; 330; 333; 340; 345; 385; 444; 61; 66; ELLIPSIS",
            C_TRAIN_STATION,
        ),
    )
    @example(
        data=(
            "platform; station; 192; 196; 199; 202; 300; 301; 306; 322; 330; 60; ELLIPSIS",
            C_TRAIN_STATION,
        ),
    )
    @example(data=("station; 139; 169; 192; 209; 28; 29; 66; P332", C_TRAIN_STATION))
    @example(
        data=(
            "station; 111; 114; 120; 121; 139; 160; 161; 169; 170; ELLIPSIS",
            C_TRAIN_STATION,
        ),
    )
    @example(
        data=(
            "platform; station; 100; 110; 113; 115; 117; 124; 125; 172; 174; ELLIPSIS",
            C_TRAIN_STATION,
        ),
    )
    @example(data=("platform; station; Ipswich/Rosewood Line", C_TRAIN_STATION))
    @example(data=("platform; station; Sunshine Coast Line", C_TRAIN_STATION))

    # CATEGORY_TRAIN_CARPARK
    @example(
        data=(
            "park 'n' ride; station; 526; 528; 531; 533; 534; Springfield Line",
            C_TRAIN_CARPARK,
        ),
    )

    # CATEGORY_TRAIN_ACCESSIBILITY

    # CATEGORY_BUS_STOP
    @example(
        data=("bus station; 327; 338; 669; 670; 671; 672; 673; 674; 680", C_BUS_STOP),
    )
    @example(data=("station; stop; 680", C_BUS_STOP))
    @example(data=("bus stop; station; 649", C_BUS_STOP))
    @example(data=("station; stop; 4251; 4429; 4494; 550; 561", C_BUS_STOP))
    @example(data=("station; stop; 562; 563", C_BUS_STOP))
    @example(data=("stop; 553", C_BUS_STOP))
    @example(data=("stop; 192; 60", C_BUS_STOP))
    @example(data=("stop; 470", C_BUS_STOP))
    @example(data=("stop; 354", C_BUS_STOP))
    @example(data=("stop; 227; 240; 5014; 5076; 5077; 5078; 5089", C_BUS_STOP))
    @example(data=("stop; 180; 185; P179", C_BUS_STOP))
    @example(data=("stop; 5721; 609", C_BUS_STOP))
    @example(
        data=(
            "stop; 4210; 4212; 4214; 4215; 576; 577; 8025; 8029; ELLIPSIS",
            C_BUS_STOP,
        ),
    )
    @example(
        data=(
            "service; stop; ELLIPSIS; N100; N111; N130; N154; N184; N199; N200; N226",
            C_BUS_STOP,
        ),
    )
    @example(
        data=("stop; 3009; 3048; 3307; 3384; 700; 760; 767; 768; ELLIPSIS", C_BUS_STOP),
    )
    @example(data=("stop; 224", C_BUS_STOP))
    @example(
        data=(
            "stop; 4170; 4270; 4271; 4405; 4407; 563; 564; 568; ELLIPSIS",
            C_BUS_STOP,
        ),
    )
    @example(data=("stop; 608", C_BUS_STOP))
    @example(data=("stop; 4428; 4492; 560; 6055; 6155", C_BUS_STOP))
    @example(
        data=(
            "stop; 105; 107; 108; 112; 113; 172; 174; 175; 192; 60; ELLIPSIS",
            C_BUS_STOP,
        ),
    )
    @example(data=("stop; 104; 105; 107; 108; 196", C_BUS_STOP))
    @example(
        data=(
            "stop; 5201; 5202; 5203; 5205; 5210; 5211; 5212; 524; ELLIPSIS",
            C_BUS_STOP,
        ),
    )
    @example(data=("stop; 719", C_BUS_STOP))
    @example(data=("stop; 3009; 700; 765", C_BUS_STOP))
    @example(data=("stop; 4417; 4462; 560; 562; 564", C_BUS_STOP))
    @example(data=("stop; 3024; 3338; 3415; 3430; 3436; 741", C_BUS_STOP))
    @example(
        data=(
            "stop; 5709; 5721; 5730; 5731; 5733; 604; 606; 608; ELLIPSIS",
            C_BUS_STOP,
        ),
    )
    @example(data=("stop; 120; 123; 125; 134; 135; 145; 155; N154", C_BUS_STOP))
    @example(data=("stop; 701; 704; 706; 707; 790", C_BUS_STOP))
    @example(data=("stop; 415; 433; 445", C_BUS_STOP))
    @example(data=("stop; 333; 340; 370; 77; P332", C_BUS_STOP))
    @example(
        data=(
            "stop; 250; 270; 279; 280; 281; 282; 5040; 5050; 5051; ELLIPSIS",
            C_BUS_STOP,
        ),
    )
    @example(data=("stop; 700; 777", C_BUS_STOP))
    @example(data=("stop; 308; 370; N339", C_BUS_STOP))
    @example(data=("stop; 5730; 5738; 604", C_BUS_STOP))
    @example(data=("stop; 300; 373", C_BUS_STOP))
    @example(data=("stop; 7022; 7027; 7038; 7043; 7045", C_BUS_STOP))
    @example(
        data=(
            "stop; 4170; 4270; 4271; 4405; 4407; 563; 564; 568; ELLIPSIS",
            C_BUS_STOP,
        ),
    )
    @example(data=("stop; 534", C_BUS_STOP))
    @example(data=("stop; 907", C_BUS_STOP))
    @example(data=("stop; 901; 902; 905", C_BUS_STOP))
    @example(data=("stop; 905", C_BUS_STOP))
    @example(data=("stop; 700", C_BUS_STOP))
    @example(data=("stop; 700; 765; 777", C_BUS_STOP))
    @example(data=("stop; 104; 105; 108; 109", C_BUS_STOP))
    @example(data=("bus stop; 192; 199; 60; N199", C_BUS_STOP))
    @example(data=("stop; 397; 905; 910; 912; 920", C_BUS_STOP))
    @example(data=("stop; 3104; 3338; 3445; 704", C_BUS_STOP))
    @example(data=("stop; 425; 428; 430; 433; 444; 453; 454; 460", C_BUS_STOP))
    @example(data=("stop; 113; 845; 847; 849", C_BUS_STOP))
    @example(data=("stop; 250; 271; 274; N250", C_BUS_STOP))
    @example(data=("stop; 367; 397; 398", C_BUS_STOP))
    @example(data=("stop; 907", C_BUS_STOP))
    @example(data=("stop; 5706; 5721; 5737", C_BUS_STOP))
    @example(data=("stop; 143; 143W", C_BUS_STOP))
    @example(data=("stop; 904", C_BUS_STOP))
    @example(data=("stop; 299; 578; 579", C_BUS_STOP))
    @example(data=("stop; 542", C_BUS_STOP))
    @example(data=("route; stops; 326", C_BUS_STOP))
    @example(data=("stop; 5781; 5786; 618", C_BUS_STOP))
    @example(data=("stop; 750", C_BUS_STOP))
    @example(data=("stop; 554; 8033", C_BUS_STOP))
    @example(data=("stops; 143", C_BUS_STOP))
    @example(data=("stop; 669; 671; 672; 673; 6800; 6808", C_BUS_STOP))
    @example(data=("stop; 680; 6840; 6871", C_BUS_STOP))
    @example(data=("stop; 204; 208", C_BUS_STOP))
    @example(data=("stop; 541; 6043; 6151", C_BUS_STOP))
    @example(data=("stop; 690; 694; 696", C_BUS_STOP))
    @example(data=("stop; 403; 407", C_BUS_STOP))

    # CATEGORY_FERRY_TERMINAL

    # CATEGORY_TRAIN_SERVICE
    @example(data=("line; timetable; Beenleigh Line", C_TRAIN_SERVICE))
    @example(
        data=(
            "ELLIPSIS; Airport Line; Beenleigh Line; Caboolture Line",
            C_TRAIN_SERVICE,
        ),
    )

    # CATEGORY_BUS_SERVICE
    @example(data=("bus routes; 720; 721; 724; Gold Coast Line", C_BUS_SERVICE))
    @example(data=("timetable; 301; 302; 303; 305; 306; 308", C_BUS_SERVICE))
    @example(data=("700; 777", C_BUS_SERVICE))
    @example(
        data=("747; 748; 750; 751; 753; 757; 759; 760; 765; ELLIPSIS", C_BUS_SERVICE),
    )
    @example(data=("bus services; 721; 722; 726", C_BUS_SERVICE))
    @example(data=("service; KGT", C_BUS_SERVICE))
    @example(
        data=(
            "timetables; 602; 603; 607; 610; 612; 614; 615; 616; 617; ELLIPSIS",
            C_BUS_SERVICE,
        ),
    )
    @example(
        data=(
            "timetables; 713; 714; 715; 717; 718; 719; 721; 722; 723; ELLIPSIS",
            C_BUS_SERVICE,
        ),
    )
    @example(data=("626; 627; 628; 629; 632", C_BUS_SERVICE))
    @example(data=("route; service; 203", C_BUS_SERVICE))
    @example(data=("route; P569", C_BUS_SERVICE))

    # CATEGORY_FERRY_SERVICE
    @example(data=("services; Southern Moreton Bay Island Ferry", C_FERRY_SERVICE))
    @example(
        data=("timetable; Bulimba to Teneriffe Cross River Ferry", C_FERRY_SERVICE)
    )
    def test_transport_event_category_guess(self, data: tuple[str, str]):
        if not data:
            return
        raw, actual = data
        assert transport_models.Event.guess_category(raw) == actual

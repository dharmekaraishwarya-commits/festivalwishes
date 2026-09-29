# ```python
import csv
import os

from django.core.management.base import BaseCommand, CommandError
from django.utils.dateparse import parse_datetime
from django.utils.text import slugify

from wishes.models import Festival


class Command(BaseCommand):

    help = "Import festivals from CSV file"

    def add_arguments(self, parser):

        parser.add_argument(
            "csv_file",
            type=str,
            help="CSV file path"
        )

        parser.add_argument(
            "--update",
            action="store_true",
            help="Update existing festivals"
        )

    def handle(self, *args, **options):

        csv_file = options["csv_file"]
        update_existing = options["update"]

        # -----------------------------------
        # CHECK FILE
        # -----------------------------------

        if not os.path.exists(csv_file):

            raise CommandError(
                f"CSV file not found: {csv_file}"
            )

        imported = 0
        updated = 0
        skipped = 0
        errors = 0

        # -----------------------------------
        # OPEN CSV
        # -----------------------------------

        try:

            with open(
                csv_file,
                "r",
                encoding="utf-8-sig",
                newline=""
            ) as file:

                reader = csv.DictReader(file)

                # -----------------------------------
                # CLEAN CSV HEADERS
                # -----------------------------------

                if not reader.fieldnames:

                    raise CommandError(
                        "CSV file has no header row."
                    )

                reader.fieldnames = [
                    header.strip().lower()
                    for header in reader.fieldnames
                    if header
                ]

                self.stdout.write(
                    self.style.SUCCESS(
                        "CSV columns detected:"
                    )
                )

                self.stdout.write(
                    ", ".join(reader.fieldnames)
                )

                # -----------------------------------
                # REQUIRED COLUMNS
                # -----------------------------------

                required_columns = [

                    "name",
                    "slug",
                    "date",

                    "heading",

                    "message_1",
                    "message_2",
                    "message_3",
                    "message_4",

                    "theme_color",

                    "animation",

                    "views",

                    "is_trending",

                    "is_active",
                ]

                missing_columns = [

                    column
                    for column in required_columns
                    if column not in reader.fieldnames

                ]

                if missing_columns:

                    raise CommandError(
                        "Missing CSV columns: "
                        + ", ".join(missing_columns)
                    )

                # -----------------------------------
                # PROCESS ROWS
                # -----------------------------------

                for row_number, row in enumerate(
                    reader,
                    start=2
                ):

                    try:

                        # -----------------------------------
                        # NAME
                        # -----------------------------------

                        name = (
                            row.get("name", "")
                            .strip()
                        )

                        if not name:

                            raise ValueError(
                                "Festival name is empty"
                            )

                        # -----------------------------------
                        # SLUG
                        # -----------------------------------

                        slug = (
                            row.get("slug", "")
                            .strip()
                        )

                        if not slug:

                            slug = slugify(name)

                        # -----------------------------------
                        # DATE
                        # -----------------------------------

                        date_string = (
                            row.get("date", "")
                            .strip()
                        )

                        festival_date = parse_datetime(
                            date_string
                        )

                        if festival_date is None:

                            raise ValueError(
                                f"Invalid date: {date_string}"
                            )

                        # -----------------------------------
                        # TEXT
                        # -----------------------------------

                        heading = (
                            row.get("heading", "")
                            .strip()
                        )

                        message_1 = (
                            row.get("message_1", "")
                            .strip()
                        )

                        message_2 = (
                            row.get("message_2", "")
                            .strip()
                        )

                        message_3 = (
                            row.get("message_3", "")
                            .strip()
                        )

                        message_4 = (
                            row.get("message_4", "")
                            .strip()
                        )

                        # -----------------------------------
                        # THEME COLOR
                        # -----------------------------------

                        theme_color = (
                            row.get("theme_color", "")
                            .strip()
                        )

                        if not theme_color:

                            theme_color = "#ff9800"

                        # -----------------------------------
                        # ANIMATION
                        # -----------------------------------

                        animation = (
                            row.get("animation", "")
                            .strip()
                            .lower()
                        )

                        if not animation:

                            animation = "confetti"

                        valid_animations = [

                            choice[0]
                            for choice
                            in Festival.ANIMATION_CHOICES

                        ]

                        if animation not in valid_animations:

                            raise ValueError(
                                f"Invalid animation: "
                                f"{animation}. "
                                f"Use one of: "
                                f"{', '.join(valid_animations)}"
                            )

                        # -----------------------------------
                        # VIEWS
                        # -----------------------------------

                        views_string = (
                            row.get("views", "0")
                            .strip()
                        )

                        if not views_string:

                            views = 0

                        else:

                            views = int(
                                views_string
                            )

                        # -----------------------------------
                        # TRENDING
                        # -----------------------------------

                        trending_value = (

                            row.get(
                                "is_trending",
                                "false"
                            )
                            .strip()
                            .lower()

                        )

                        is_trending = (

                            trending_value
                            in [
                                "1",
                                "true",
                                "yes",
                                "y"
                            ]

                        )

                        # -----------------------------------
                        # ACTIVE
                        # -----------------------------------

                        active_value = (

                            row.get(
                                "is_active",
                                "true"
                            )
                            .strip()
                            .lower()

                        )

                        is_active = (

                            active_value
                            in [
                                "1",
                                "true",
                                "yes",
                                "y"
                            ]

                        )

                        # -----------------------------------
                        # DATA
                        # -----------------------------------

                        festival_data = {

                            "name": name,

                            "slug": slug,

                            "date": festival_date,

                            "heading": heading,

                            "message_1": message_1,
                            "message_2": message_2,
                            "message_3": message_3,
                            "message_4": message_4,

                            "theme_color": theme_color,

                            "animation": animation,

                            "views": views,

                            "is_trending": is_trending,

                            "is_active": is_active,

                        }

                        # -----------------------------------
                        # FIND EXISTING FESTIVAL
                        # -----------------------------------

                        festival = (
                            Festival.objects
                            .filter(slug=slug)
                            .first()
                        )

                        # -----------------------------------
                        # UPDATE
                        # -----------------------------------

                        if festival:

                            if update_existing:

                                for field, value in (
                                    festival_data.items()
                                ):

                                    setattr(
                                        festival,
                                        field,
                                        value
                                    )

                                festival.save()

                                updated += 1

                                self.stdout.write(

                                    self.style.WARNING(

                                        f"UPDATED: {name}"

                                    )

                                )

                            else:

                                skipped += 1

                                self.stdout.write(

                                    self.style.WARNING(

                                        f"SKIPPED: {name} "
                                        f"(already exists)"

                                    )

                                )

                        # -----------------------------------
                        # CREATE
                        # -----------------------------------

                        else:

                            Festival.objects.create(
                                **festival_data
                            )

                            imported += 1

                            self.stdout.write(

                                self.style.SUCCESS(

                                    f"IMPORTED: {name}"

                                )

                            )

                    except Exception as error:

                        errors += 1

                        self.stdout.write(

                            self.style.ERROR(

                                f"ROW {row_number}: "
                                f"{error}"

                            )

                        )

        except UnicodeDecodeError:

            raise CommandError(

                "CSV encoding error. "
                "Save the CSV as UTF-8."

            )

        # -----------------------------------
        # SUMMARY
        # -----------------------------------

        self.stdout.write("")

        self.stdout.write(
            self.style.SUCCESS(
                "================================"
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                " FESTIVAL IMPORT COMPLETE"
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                "================================"
            )
        )

        self.stdout.write(
            f"Imported : {imported}"
        )

        self.stdout.write(
            f"Updated  : {updated}"
        )

        self.stdout.write(
            f"Skipped  : {skipped}"
        )

        self.stdout.write(
            f"Errors   : {errors}"
        )

        self.stdout.write(
            self.style.SUCCESS(
                "================================"
            )
        )






# new 



# import pandas as pd
# from pathlib import Path

# columns = [
#     "name","slug","date","heading","message_1","message_2","message_3",
#     "message_4","theme_color","animation","views","is_trending","is_active"
# ]

# events = [
#     # 2026 remaining
#     ("Pitrupaksha Begins","2026-09-27","#5d4037","Pitrupaksha Begins",
#      "May Pitrupaksha bring peace to departed souls and blessings to every family.",
#      "Wishing you a time of remembrance, gratitude and devotion.",
#      "May ancestral blessings bring strength, harmony and positivity into your home.",
#      "Have a peaceful and blessed Pitrupaksha."),
#     ("Indira Ekadashi","2026-10-06","#1565c0","Happy Indira Ekadashi",
#      "May Lord Vishnu bless your family with peace, devotion and prosperity.",
#      "Wishing you strength, faith and positivity on this sacred Ekadashi.",
#      "May your prayers bring divine grace and happiness into your life.",
#      "Have a blessed Indira Ekadashi."),
#     ("Sarva Pitru Amavasya","2026-10-10","#4e342e","Sarva Pitru Amavasya",
#      "May the blessings of your ancestors bring peace and harmony to your family.",
#      "Wishing you a day of remembrance, gratitude and devotion.",
#      "May your prayers bring strength, serenity and family unity.",
#      "Have a peaceful Sarva Pitru Amavasya."),
#     ("Navratri","2026-10-11","#c2185b","Jai Mata Di",
#      "May Maa Durga bless you with strength, courage and happiness.",
#      "May these nine sacred nights fill your home with devotion and positive energy.",
#      "Wishing you prosperity, peace and countless reasons to celebrate.",
#      "Have a divine and joyful Navratri."),
#     ("Saraswati Avahan","2026-10-16","#f4c430","Saraswati Avahan",
#      "May Goddess Saraswati bless you with wisdom, creativity and knowledge.",
#      "Wishing every learner and creator inspiration and confidence.",
#      "May the light of knowledge guide every step of your journey.",
#      "Have a blessed Saraswati Avahan."),
#     ("Saraswati Puja","2026-10-17","#f4c430","Happy Saraswati Puja",
#      "May Goddess Saraswati bless your life with wisdom and creativity.",
#      "Wishing you knowledge, learning and inspiration in everything you do.",
#      "May your mind remain curious, focused and filled with positive thoughts.",
#      "Have a blessed Saraswati Puja."),
#     ("Durga Ashtami","2026-10-19","#b71c1c","Jai Mata Di",
#      "May Maa Durga bless you with courage, strength and protection.",
#      "May divine Shakti fill your heart with confidence and positivity.",
#      "Wishing your family peace, prosperity and happiness.",
#      "Have a blessed Durga Ashtami."),
#     ("Maha Navami","2026-10-19","#d32f2f","Jai Mata Di",
#      "May Maa Durga bless your family with strength and divine grace.",
#      "Wishing you courage to overcome every challenge.",
#      "May your home be filled with happiness, devotion and positive energy.",
#      "Have a blessed Maha Navami."),
#     ("Dussehra","2026-10-20","#ef6c00","Happy Dussehra",
#      "May truth, courage and positive thoughts always triumph in your life.",
#      "Wishing you success, happiness and strength to overcome every obstacle.",
#      "May this Dussehra bring new beginnings and brighter days.",
#      "Happy Dussehra!"),
#     ("Papankusha Ekadashi","2026-10-22","#1565c0","Happy Papankusha Ekadashi",
#      "May Lord Vishnu bless you with peace, devotion and wisdom.",
#      "Wishing you strength and positivity on this sacred day.",
#      "May your prayers bring clarity and divine grace.",
#      "Have a blessed Papankusha Ekadashi."),
#     ("Kojagara Puja","2026-10-25","#7b1fa2","Happy Kojagara Puja",
#      "May Goddess Lakshmi bless your home with prosperity and happiness.",
#      "Wishing your family abundance, peace and togetherness.",
#      "May every prayer bring new opportunities and positivity.",
#      "Have a blessed Kojagara Puja."),
#     ("Sharad Purnima","2026-10-25","#5e35b1","Happy Sharad Purnima",
#      "May the beautiful full moon fill your life with peace and positivity.",
#      "Wishing your family happiness, health and prosperity.",
#      "May this sacred night bring divine blessings and beautiful memories.",
#      "Have a blessed Sharad Purnima."),
#     ("Karwa Chauth","2026-10-29","#ad1457","Happy Karwa Chauth",
#      "May love, trust and togetherness grow stronger every day.",
#      "Wishing couples happiness, health and beautiful memories together.",
#      "May your family always be surrounded by love and prosperity.",
#      "Have a blessed Karwa Chauth."),
#     ("Ahoi Ashtami","2026-11-01","#8e24aa","Happy Ahoi Ashtami",
#      "May Ahoi Mata bless every family with happiness, health and protection.",
#      "Wishing children a bright future filled with love and success.",
#      "May your home always be filled with laughter and togetherness.",
#      "Have a blessed Ahoi Ashtami."),
#     ("Govatsa Dwadashi","2026-11-05","#388e3c","Happy Govatsa Dwadashi",
#      "May this sacred day bring compassion, prosperity and harmony to your home.",
#      "Wishing your family health, happiness and abundance.",
#      "May gratitude and kindness brighten every day.",
#      "Have a blessed Govatsa Dwadashi."),
#     ("Rama Ekadashi","2026-11-05","#1565c0","Happy Rama Ekadashi",
#      "May Lord Vishnu bless your family with peace, strength and prosperity.",
#      "Wishing you devotion, clarity and positive energy.",
#      "May your prayers bring happiness and divine guidance.",
#      "Have a blessed Rama Ekadashi."),
#     ("Dhanteras","2026-11-06","#d4af37","Happy Dhanteras",
#      "May Goddess Lakshmi and Lord Dhanvantari bless your home with prosperity and health.",
#      "Wishing you wealth, happiness and success in every new beginning.",
#      "May your family always enjoy abundance, good health and peace.",
#      "Have a prosperous Dhanteras."),
#     ("Kali Chaudas","2026-11-07","#212121","Happy Kali Chaudas",
#      "May divine strength remove negativity and fear from your life.",
#      "Wishing you courage, peace and positive energy.",
#      "May your home remain protected and filled with light.",
#      "Have a blessed Kali Chaudas."),
#     ("Lakshmi Puja","2026-11-08","#d4af37","Happy Lakshmi Puja",
#      "May Goddess Lakshmi bless your home with wealth, peace and prosperity.",
#      "Wishing your family abundance, happiness and success.",
#      "May every diya bring hope and positivity into your life.",
#      "Shubh Lakshmi Puja."),
#     ("Narak Chaturdashi","2026-11-08","#ff6f00","Happy Narak Chaturdashi",
#      "May every form of negativity disappear from your life.",
#      "Wishing you happiness, peace and a heart full of positive thoughts.",
#      "May divine light guide your family toward brighter days.",
#      "Have a blessed Narak Chaturdashi."),
#     ("Diwali","2026-11-08","#7a1738","Happy Diwali",
#      "May the festival of lights fill your home with happiness, love and prosperity.",
#      "Wishing you beautiful memories, success and togetherness with your family.",
#      "May every diya brighten your path and every smile make your celebration special.",
#      "Shubh Deepavali!"),
#     ("Govardhan Puja","2026-11-10","#2e7d32","Happy Govardhan Puja",
#      "May Lord Krishna bless your family with prosperity, protection and happiness.",
#      "Wishing you abundance, gratitude and beautiful moments together.",
#      "May devotion and kindness always guide your path.",
#      "Have a blessed Govardhan Puja."),
#     ("Bhai Dooj","2026-11-11","#6a1b9a","Happy Bhai Dooj",
#      "May the beautiful bond between brothers and sisters grow stronger every day.",
#      "Wishing your family endless love, laughter and togetherness.",
#      "May this special relationship always bring happiness and support.",
#      "Happy Bhai Dooj!"),
#     ("Chhath Puja","2026-11-15","#e65100","Jai Chhathi Maiya",
#      "May Chhathi Maiya bless your family with health, prosperity and happiness.",
#      "Wishing you devotion, peace and strength on this sacred occasion.",
#      "May the rising Sun fill your life with hope and positive energy.",
#      "Have a blessed Chhath Puja."),
#     ("Kansa Vadh","2026-11-20","#5d4037","Kansa Vadh",
#      "May Lord Krishna inspire courage and righteousness in your life.",
#      "Wishing you strength to overcome negativity and challenges.",
#      "May truth, faith and devotion always guide your family.",
#      "Have a blessed Kansa Vadh."),
#     ("Devutthana Ekadashi","2026-11-20","#1565c0","Happy Devutthana Ekadashi",
#      "May Lord Vishnu bless your home with peace, prosperity and devotion.",
#      "Wishing you fresh beginnings filled with hope and positivity.",
#      "May divine blessings guide every step of your journey.",
#      "Have a blessed Devutthana Ekadashi."),
#     ("Tulasi Vivah","2026-11-21","#388e3c","Happy Tulasi Vivah",
#      "May Tulsi Mata bless your home with peace, harmony and prosperity.",
#      "Wishing your family happiness, good fortune and togetherness.",
#      "May devotion bring divine blessings into your life.",
#      "Have a blessed Tulasi Vivah."),
#     ("Kartika Purnima","2026-11-24","#5e35b1","Happy Kartika Purnima",
#      "May this sacred full moon bring peace, prosperity and divine blessings.",
#      "Wishing your family happiness, health and spiritual growth.",
#      "May your home shine with positivity and hope.",
#      "Have a blessed Kartika Purnima."),
#     ("Guru Nanak Jayanti","2026-11-24","#1565c0","Happy Gurpurab",
#      "May Guru Nanak Dev Ji's teachings inspire peace, kindness and compassion.",
#      "Wishing you humility, happiness and harmony in every part of life.",
#      "May your path always be guided by truth and service.",
#      "Waheguru Ji Ka Khalsa, Waheguru Ji Ki Fateh!"),
#     ("Kalabhairav Jayanti","2026-12-01","#37474f","Jai Kalabhairav",
#      "May Lord Kalabhairav bless you with courage, protection and wisdom.",
#      "Wishing you strength to face every challenge with faith.",
#      "May your family remain surrounded by peace and divine grace.",
#      "Have a blessed Kalabhairav Jayanti."),
#     ("Utpanna Ekadashi","2026-12-04","#1565c0","Happy Utpanna Ekadashi",
#      "May Lord Vishnu bless your life with devotion, peace and wisdom.",
#      "Wishing you strength, clarity and positivity.",
#      "May your prayers bring divine grace and happiness to your family.",
#      "Have a blessed Utpanna Ekadashi."),
#     ("Vivah Panchami","2026-12-14","#8e24aa","Happy Vivah Panchami",
#      "May the divine union of Shri Ram and Mata Sita inspire love and harmony.",
#      "Wishing your family peace, devotion and happiness.",
#      "May every relationship be blessed with understanding and respect.",
#      "Have a blessed Vivah Panchami."),
#     ("Dhanu Sankranti","2026-12-16","#ff9800","Happy Dhanu Sankranti",
#      "May the Sun bring warmth, health and prosperity to your family.",
#      "Wishing you positive energy and successful new beginnings.",
#      "May every day ahead be filled with hope and happiness.",
#      "Have a blessed Dhanu Sankranti."),
#     ("Gita Jayanti","2026-12-20","#8d6e63","Happy Gita Jayanti",
#      "May the wisdom of the Bhagavad Gita guide your thoughts and actions.",
#      "Wishing you courage, clarity and inner peace.",
#      "May every challenge become an opportunity to learn and grow.",
#      "Have a blessed Gita Jayanti."),
#     ("Mokshada Ekadashi","2026-12-20","#1565c0","Happy Mokshada Ekadashi",
#      "May Lord Vishnu bless your family with peace and spiritual strength.",
#      "Wishing you devotion, wisdom and positive thoughts.",
#      "May your prayers bring clarity and divine grace.",
#      "Have a blessed Mokshada Ekadashi."),
#     ("Dattatreya Jayanti","2026-12-23","#6a1b9a","Happy Dattatreya Jayanti",
#      "May Lord Dattatreya bless you with wisdom, peace and prosperity.",
#      "Wishing your family spiritual growth and happiness.",
#      "May divine guidance remain with you through every journey.",
#      "Have a blessed Dattatreya Jayanti."),
#     ("Christmas","2026-12-25","#c62828","Merry Christmas",
#      "May Christmas fill your home with love, peace and happiness.",
#      "Wishing you beautiful moments with family and friends.",
#      "May the season bring hope, kindness and joyful new beginnings.",
#      "Merry Christmas!"),

#     # 2027
#     ("New Year","2027-01-01","#3f51b5","Happy New Year",
#      "May the new year bring happiness, health, success and fresh opportunities.",
#      "Wishing you beautiful beginnings and countless memorable moments.",
#      "May every day bring a new reason to smile and grow.",
#      "Happy New Year!"),
#     ("Saphala Ekadashi","2027-01-03","#1565c0","Happy Saphala Ekadashi",
#      "May Lord Vishnu bless your efforts with success and peace.",
#      "Wishing you strength, devotion and positive beginnings.",
#      "May your sincere efforts lead to beautiful results.",
#      "Have a blessed Saphala Ekadashi."),
#     ("Swami Vivekananda Jayanti","2027-01-12","#ff9800","Swami Vivekananda Jayanti",
#      "May the teachings of Swami Vivekananda inspire courage and self-belief.",
#      "Wishing you strength, knowledge and determination.",
#      "May every dream be pursued with confidence and purpose.",
#      "Let inspiration lead you toward greatness."),
#     ("Lohri","2027-01-14","#e65100","Happy Lohri",
#      "May the warmth of Lohri fill your home with happiness and togetherness.",
#      "Wishing you prosperity, health and joyful celebrations.",
#      "May the bonfire carry away negativity and welcome positivity.",
#      "Happy Lohri!"),
#     ("Guru Gobind Singh Jayanti","2027-01-15","#1565c0","Guru Gobind Singh Jayanti",
#      "May Guru Gobind Singh Ji inspire courage, compassion and truth.",
#      "Wishing your family strength, peace and faith.",
#      "May his teachings guide you toward a life of dignity and service.",
#      "Waheguru Ji Ka Khalsa, Waheguru Ji Ki Fateh!"),
#     ("Makar Sankranti","2027-01-15","#ff9800","Happy Makar Sankranti",
#      "May the Sun God bless your family with health, prosperity and happiness.",
#      "Wishing you warmth, success and bright new beginnings.",
#      "May every new day bring positive energy and opportunities.",
#      "Happy Makar Sankranti!"),
#     ("Pongal","2027-01-15","#f57c00","Happy Pongal",
#      "May Pongal bring abundance, happiness and prosperity to your home.",
#      "Wishing your family a joyful harvest celebration filled with love.",
#      "May your life always be as sweet and bright as the festival.",
#      "Happy Pongal!"),
#     ("Pausha Putrada Ekadashi","2027-01-18","#1565c0","Happy Pausha Putrada Ekadashi",
#      "May Lord Vishnu bless your family with happiness and peace.",
#      "Wishing your home health, prosperity and harmony.",
#      "May your prayers bring divine blessings and positive energy.",
#      "Have a blessed Ekadashi."),
#     ("Tailang Swami Jayanti","2027-01-19","#6a1b9a","Tailang Swami Jayanti",
#      "May the life and wisdom of Tailang Swami inspire peace and devotion.",
#      "Wishing you spiritual strength and inner calm.",
#      "May your journey be filled with wisdom and compassion.",
#      "Have a blessed Jayanti."),
#     ("Pausha Purnima","2027-01-22","#5e35b1","Happy Pausha Purnima",
#      "May the sacred full moon bring peace, prosperity and divine blessings.",
#      "Wishing your family health, happiness and spiritual growth.",
#      "May your prayers fill your home with positivity.",
#      "Have a blessed Pausha Purnima."),
#     ("Subhas Chandra Bose Jayanti","2027-01-23","#b71c1c","Netaji Jayanti",
#      "May Netaji's courage and dedication inspire us to serve with determination.",
#      "Wishing you strength, discipline and confidence.",
#      "May every challenge become an opportunity to act with courage.",
#      "Remembering Netaji with respect."),
#     ("Republic Day","2027-01-26","#1565c0","Happy Republic Day",
#      "May our nation continue to grow with unity, peace and progress.",
#      "Wishing everyone pride, responsibility and hope for a brighter future.",
#      "May the spirit of our Constitution inspire equality and harmony.",
#      "Happy Republic Day!"),
#     ("Sakat Chauth","2027-01-25","#e65100","Happy Sakat Chauth",
#      "May Lord Ganesha remove obstacles and bless your family with happiness.",
#      "Wishing children health, success and a bright future.",
#      "May your prayers bring strength, prosperity and peace.",
#      "Have a blessed Sakat Chauth."),
#     ("Shattila Ekadashi","2027-02-02","#1565c0","Happy Shattila Ekadashi",
#      "May Lord Vishnu bless you with peace, devotion and wisdom.",
#      "Wishing you kindness, generosity and positive energy.",
#      "May your good deeds bring happiness to your life and others.",
#      "Have a blessed Shattila Ekadashi."),
#     ("Mauni Amavasya","2027-02-06","#4e342e","Happy Mauni Amavasya",
#      "May this sacred day bring silence, reflection and inner peace.",
#      "Wishing you clarity of thought and spiritual strength.",
#      "May your prayers and self-reflection bring renewed positivity.",
#      "Have a peaceful Mauni Amavasya."),
#     ("Vasant Panchami","2027-02-11","#f4c430","Happy Vasant Panchami",
#      "May Goddess Saraswati bless you with wisdom, creativity and knowledge.",
#      "Wishing students and creators inspiration and confidence.",
#      "May your life bloom with learning, happiness and success.",
#      "Have a blessed Vasant Panchami."),
#     ("Ratha Saptami","2027-02-13","#ffb300","Happy Ratha Saptami",
#      "May the Sun God bless you with health, energy and prosperity.",
#      "Wishing you positive thoughts and fresh opportunities.",
#      "May every new day bring warmth, confidence and success.",
#      "Have a blessed Ratha Saptami."),
#     ("Bhishma Ashtami","2027-02-14","#795548","Bhishma Ashtami",
#      "May the devotion and wisdom of Bhishma inspire strength and righteousness.",
#      "Wishing you patience, courage and clarity in every decision.",
#      "May your life be guided by truth and responsibility.",
#      "Have a blessed Bhishma Ashtami."),
#     ("Jaya Ekadashi","2027-02-17","#1565c0","Happy Jaya Ekadashi",
#      "May Lord Vishnu bless your life with peace and spiritual strength.",
#      "Wishing you devotion, clarity and positive energy.",
#      "May every sincere prayer bring divine grace.",
#      "Have a blessed Jaya Ekadashi."),
#     ("Magha Purnima","2027-02-20","#5e35b1","Happy Magha Purnima",
#      "May this sacred full moon bring peace, prosperity and blessings.",
#      "Wishing your family happiness, health and spiritual growth.",
#      "May your heart remain filled with kindness and positivity.",
#      "Have a blessed Magha Purnima."),
#     ("Maha Shivaratri","2027-03-06","#263238","Har Har Mahadev",
#      "May Lord Shiva bless you with peace, strength and devotion.",
#      "Om Namah Shivaya! May your heart remain calm and courageous.",
#      "May Mahadev guide you through every challenge.",
#      "Have a blessed Maha Shivaratri."),
#     ("Amalaki Ekadashi","2027-03-18","#388e3c","Happy Amalaki Ekadashi",
#      "May Lord Vishnu bless your life with health, peace and prosperity.",
#      "Wishing you devotion, positivity and spiritual strength.",
#      "May your prayers bring clarity and happiness.",
#      "Have a blessed Amalaki Ekadashi."),
#     ("Holika Dahan","2027-03-21","#d84315","Happy Holika Dahan",
#      "May the sacred fire burn away negativity and welcome positivity.",
#      "Wishing you peace, courage and happiness.",
#      "May truth and goodness always shine in your life.",
#      "Have a blessed Holika Dahan."),
#     ("Holi","2027-03-22","#e91e63","Happy Holi",
#      "May your life be filled with vibrant colours, laughter and happiness.",
#      "Celebrate with love, friendship and beautiful memories.",
#      "May every colour bring a new reason to smile.",
#      "Happy Holi!"),
#     ("Sheetala Ashtami","2027-03-30","#2e7d32","Happy Sheetala Ashtami",
#      "May Sheetala Mata bless your family with health and peace.",
#      "Wishing your home happiness, protection and harmony.",
#      "May your family remain surrounded by wellness and positivity.",
#      "Have a blessed Sheetala Ashtami."),
#     ("Ugadi","2027-04-07","#2e7d32","Happy Ugadi",
#      "May the new year bring happiness, prosperity and success.",
#      "Wishing you fresh beginnings filled with hope and positivity.",
#      "May every day of the new year become meaningful and joyful.",
#      "Have a blessed Ugadi!"),
#     ("Gudi Padwa","2027-04-07","#ff9800","Happy Gudi Padwa",
#      "May the new year bring prosperity, happiness and bright opportunities.",
#      "Wishing your family a year filled with health and success.",
#      "May your home always be filled with positive energy.",
#      "Happy Gudi Padwa!"),
#     ("Chaitra Navratri","2027-04-07","#c2185b","Jai Mata Di",
#      "May Maa Durga bless you with strength, courage and devotion.",
#      "May these sacred nine days bring peace and positive energy.",
#      "Wishing your family happiness, prosperity and divine protection.",
#      "Have a blessed Chaitra Navratri."),
#     ("Gauri Puja","2027-04-09","#ad1457","Happy Gauri Puja",
#      "May Goddess Gauri bless your home with love and harmony.",
#      "Wishing your family happiness, prosperity and beautiful relationships.",
#      "May every prayer bring peace and divine grace.",
#      "Have a blessed Gauri Puja."),
#     ("Gangaur","2027-04-09","#ad1457","Happy Gangaur",
#      "May Goddess Gauri bless your family with love, harmony and happiness.",
#      "Wishing you prosperity, devotion and beautiful relationships.",
#      "May every prayer bring peace to your home.",
#      "Have a blessed Gangaur."),
#     ("Yamuna Chhath","2027-04-12","#0288d1","Happy Yamuna Chhath",
#      "May Maa Yamuna bless your family with purity, health and peace.",
#      "Wishing you happiness, prosperity and spiritual strength.",
#      "May devotion and gratitude fill your heart.",
#      "Have a blessed Yamuna Chhath."),
#     ("Solar New Year","2027-04-14","#ff9800","Happy Solar New Year",
#      "May the new solar year bring fresh hope, happiness and prosperity.",
#      "Wishing your family health, success and beautiful beginnings.",
#      "May every season ahead bring positive growth.",
#      "Happy Solar New Year!"),
#     ("Rama Navami","2027-04-15","#1565c0","Jai Shri Ram",
#      "May Lord Rama bless your life with courage, righteousness and peace.",
#      "Wishing you devotion, strength and prosperity.",
#      "May Shri Ram guide you on every path you choose.",
#      "Have a blessed Rama Navami."),
#     ("Swaminarayan Jayanti","2027-04-15","#6a1b9a","Swaminarayan Jayanti",
#      "May Bhagwan Swaminarayan bless you with peace, devotion and wisdom.",
#      "Wishing your family happiness, harmony and spiritual strength.",
#      "May good values guide every step of your journey.",
#      "Have a blessed Swaminarayan Jayanti."),
#     ("Kamada Ekadashi","2027-04-17","#1565c0","Happy Kamada Ekadashi",
#      "May Lord Vishnu bless you with peace, devotion and fulfillment.",
#      "Wishing you strength, clarity and positive beginnings.",
#      "May your sincere prayers bring divine grace.",
#      "Have a blessed Kamada Ekadashi."),
#     ("Mahavir Jayanti","2027-04-19","#00897b","Happy Mahavir Jayanti",
#      "May Lord Mahavir inspire peace, compassion, truth and non-violence.",
#      "Wishing you kindness, wisdom and harmony.",
#      "May your path always be guided by peaceful thoughts and actions.",
#      "Have a peaceful Mahavir Jayanti."),
#     ("Hanuman Jayanti","2027-04-20","#d84315","Jai Hanuman",
#      "May Lord Hanuman bless you with strength, courage and confidence.",
#      "May Bajrang Bali remove obstacles from your path.",
#      "Wishing you devotion, positivity and unwavering determination.",
#      "Jai Shri Ram! Jai Hanuman!"),
#     ("Parashurama Jayanti","2027-05-08","#6d4c41","Happy Parashurama Jayanti",
#      "May Lord Parashurama bless you with courage, wisdom and strength.",
#      "Wishing you peace, determination and righteousness.",
#      "May your actions always be guided by truth and discipline.",
#      "Have a blessed Parashurama Jayanti."),
#     ("Akshaya Tritiya","2027-05-09","#d4af37","Happy Akshaya Tritiya",
#      "May this auspicious day bring endless prosperity and happiness.",
#      "Wishing you success in every new beginning.",
#      "May your family be blessed with abundance, health and peace.",
#      "Have a prosperous Akshaya Tritiya."),
#     ("Ganga Saptami","2027-05-12","#0288d1","Happy Ganga Saptami",
#      "May Maa Ganga bless your life with purity, peace and strength.",
#      "Wishing your family health, happiness and prosperity.",
#      "May your heart remain filled with devotion and gratitude.",
#      "Have a blessed Ganga Saptami."),
#     ("Sita Navami","2027-05-14","#8e24aa","Happy Sita Navami",
#      "May Mata Sita bless your home with peace, patience and harmony.",
#      "Wishing your family love, strength and devotion.",
#      "May every relationship remain strong and filled with understanding.",
#      "Have a blessed Sita Navami."),
#     ("Mohini Ekadashi","2027-05-16","#1565c0","Happy Mohini Ekadashi",
#      "May Lord Vishnu bless your life with peace and wisdom.",
#      "Wishing you clarity, devotion and positive energy.",
#      "May your prayers bring divine guidance and happiness.",
#      "Have a blessed Mohini Ekadashi."),
#     ("Narasimha Jayanti","2027-05-18","#b71c1c","Jai Shri Narasimha",
#      "May Lord Narasimha protect you from every difficulty.",
#      "Wishing you courage, faith and divine blessings.",
#      "May truth and righteousness always guide your path.",
#      "Have a blessed Narasimha Jayanti."),
#     ("Buddha Purnima","2027-05-20","#8e24aa","Happy Buddha Purnima",
#      "May the teachings of Buddha bring peace, wisdom and compassion.",
#      "Wishing you mindfulness, kindness and inner calm.",
#      "May your journey be filled with serenity and understanding.",
#      "Have a peaceful Buddha Purnima."),
#     ("Narada Jayanti","2027-05-21","#6a1b9a","Happy Narada Jayanti",
#      "May the wisdom and devotion of Narada Muni inspire your journey.",
#      "Wishing you knowledge, faith and positive communication.",
#      "May your words always spread harmony and kindness.",
#      "Have a blessed Narada Jayanti."),
#     ("Vat Savitri Vrat","2027-06-04","#6a1b9a","Happy Vat Savitri Vrat",
#      "May Savitri Mata bless every family with happiness and harmony.",
#      "Wishing you love, health and prosperity.",
#      "May devotion and faith strengthen every relationship.",
#      "Have a blessed Vat Savitri Vrat."),
#     ("Shani Jayanti","2027-06-04","#37474f","Jai Shani Dev",
#      "May Shani Dev bless you with justice, patience and wisdom.",
#      "Wishing you strength to overcome every challenge.",
#      "May honest actions lead your life toward peace and positivity.",
#      "Jai Shani Dev!"),
#     ("Ganga Dussehra","2027-06-13","#0288d1","Happy Ganga Dussehra",
#      "May Maa Ganga bless your life with purity, peace and prosperity.",
#      "Wishing you health, happiness and spiritual strength.",
#      "May your heart remain filled with devotion and gratitude.",
#      "Have a blessed Ganga Dussehra."),
#     ("Nirjala Ekadashi","2027-06-14","#1565c0","Happy Nirjala Ekadashi",
#      "May Lord Vishnu bless you with strength, devotion and peace.",
#      "Wishing you spiritual energy and clarity of mind.",
#      "May your faith bring divine grace and positivity.",
#      "Have a blessed Nirjala Ekadashi."),
#     ("Vat Purnima Vrat","2027-06-18","#6a1b9a","Happy Vat Purnima Vrat",
#      "May Savitri Mata bless families with love, harmony and happiness.",
#      "Wishing your home health, peace and prosperity.",
#      "May devotion strengthen every bond of love and trust.",
#      "Have a blessed Vat Purnima Vrat."),
#     ("Jagannath Rath Yatra","2027-07-05","#d84315","Jai Jagannath",
#      "May Lord Jagannath bless you and your family with happiness and peace.",
#      "Wishing you devotion, prosperity and positive new beginnings.",
#      "May the divine chariot bring blessings into your life.",
#      "Jai Jagannath!"),
#     ("Devshayani Ekadashi","2027-07-14","#1565c0","Happy Devshayani Ekadashi",
#      "May Lord Vishnu bless your family with peace and devotion.",
#      "Wishing you spiritual strength and positive thoughts.",
#      "May your prayers bring divine grace and prosperity.",
#      "Have a blessed Devshayani Ekadashi."),
#     ("Guru Purnima","2027-07-18","#6a1b9a","Happy Guru Purnima",
#      "Grateful for every teacher and guide who lights our path.",
#      "May your gurus bless you with wisdom, knowledge and success.",
#      "Wishing you humility, learning and continuous growth.",
#      "Have a blessed Guru Purnima."),
#     ("Hariyali Teej","2027-08-04","#2e7d32","Happy Hariyali Teej",
#      "May Goddess Parvati bless your family with love and harmony.",
#      "Wishing you happiness, devotion and prosperity.",
#      "May every prayer bring peace and fulfillment.",
#      "Have a blessed Hariyali Teej."),
#     ("Nag Panchami","2027-08-06","#388e3c","Happy Nag Panchami",
#      "May this sacred day bring peace, protection and harmony to your family.",
#      "Wishing you prosperity and positive energy.",
#      "May we always respect nature and every living being.",
#      "Have a blessed Nag Panchami."),
#     ("Tulsidas Jayanti","2027-08-08","#6a1b9a","Tulsidas Jayanti",
#      "May the devotion and wisdom of Goswami Tulsidas inspire your life.",
#      "Wishing you faith, knowledge and inner peace.",
#      "May sacred words and good values guide your journey.",
#      "Have a blessed Tulsidas Jayanti."),
#     ("Varalakshmi Vrat","2027-08-13","#d4af37","Happy Varalakshmi Vrat",
#      "May Goddess Lakshmi bless your home with prosperity and happiness.",
#      "Wishing your family health, abundance and harmony.",
#      "May every prayer bring divine blessings and positive opportunities.",
#      "Have a prosperous Varalakshmi Vrat."),
#     ("Raksha Bandhan","2027-08-17","#ad1457","Happy Raksha Bandhan",
#      "May the bond between brothers and sisters grow stronger every day.",
#      "Wishing you endless love, laughter and beautiful memories.",
#      "May family always remain your greatest source of strength.",
#      "Happy Raksha Bandhan!"),
#     ("Gayatri Jayanti","2027-08-17","#ff9800","Happy Gayatri Jayanti",
#      "May Maa Gayatri bless you with wisdom, strength and clarity.",
#      "Wishing you peace, knowledge and positive energy.",
#      "May divine light guide your thoughts and actions.",
#      "Have a blessed Gayatri Jayanti."),
#     ("Kajari Teej","2027-08-20","#2e7d32","Happy Kajari Teej",
#      "May Goddess Parvati bless your family with love and harmony.",
#      "Wishing you happiness, prosperity and beautiful relationships.",
#      "May devotion bring peace and positivity into your home.",
#      "Have a blessed Kajari Teej."),
#     ("Janmashtami","2027-08-25","#1565c0","Hare Krishna",
#      "May Lord Krishna fill your life with love, wisdom and joy.",
#      "Wishing you peace, devotion and beautiful moments with family.",
#      "May Krishna's blessings guide you through every challenge.",
#      "Have a joyful Janmashtami."),
#     ("Aja Ekadashi","2027-08-28","#1565c0","Happy Aja Ekadashi",
#      "May Lord Vishnu bless your life with peace and spiritual strength.",
#      "Wishing you devotion, clarity and positive energy.",
#      "May your prayers bring divine guidance and happiness.",
#      "Have a blessed Aja Ekadashi."),
#     ("Hartalika Teej","2027-09-03","#e91e63","Happy Hartalika Teej",
#      "May Goddess Parvati bless your family with love and harmony.",
#      "Wishing you happiness, devotion and prosperity.",
#      "May your prayers bring peace and fulfillment.",
#      "Have a blessed Hartalika Teej."),
#     ("Ganesh Chaturthi","2027-09-04","#f57c00","Ganpati Bappa Morya",
#      "May Lord Ganesha remove obstacles and bless you with success.",
#      "Wishing your home happiness, prosperity and good fortune.",
#      "May every new beginning be filled with divine blessings.",
#      "Have a joyful Ganesh Chaturthi."),
#     ("Rishi Panchami","2027-09-04","#6a1b9a","Happy Rishi Panchami",
#      "May the wisdom of the ancient sages inspire knowledge and humility.",
#      "Wishing you peace, discipline and spiritual growth.",
#      "May your life be guided by good values and thoughtful actions.",
#      "Have a blessed Rishi Panchami."),
#     ("Balarama Jayanti","2027-09-06","#1565c0","Balarama Jayanti",
#      "May Lord Balarama bless you with strength, courage and wisdom.",
#      "Wishing your family happiness, peace and prosperity.",
#      "May devotion and righteousness guide your journey.",
#      "Have a blessed Balarama Jayanti."),
#     ("Radha Ashtami","2027-09-08","#c2185b","Radhe Radhe",
#      "May Radha Rani fill your life with love, devotion and divine grace.",
#      "Wishing you peace, happiness and spiritual joy.",
#      "May your heart always remain connected with bhakti.",
#      "Radhe Radhe!"),
#     ("Onam","2027-09-12","#2e7d32","Happy Onam",
#      "May Onam bring prosperity, happiness and togetherness to your family.",
#      "Wishing you a beautiful celebration filled with love and gratitude.",
#      "May your home always be blessed with abundance and joy.",
#      "Have a wonderful Onam!"),
#     ("Ganesh Visarjan","2027-09-14","#ff6f00","Ganpati Bappa Morya",
#      "May Bappa take away every obstacle and return with greater blessings.",
#      "Wishing you peace, prosperity and devotion.",
#      "Celebrate with gratitude and hope for a beautiful return.",
#      "Ganpati Bappa Morya!"),
#     ("Anant Chaturdashi","2027-09-14","#1565c0","Happy Anant Chaturdashi",
#      "May Lord Vishnu bless your family with peace and prosperity.",
#      "Wishing you strength, happiness and divine protection.",
#      "May your life be filled with lasting blessings and positivity.",
#      "Have a blessed Anant Chaturdashi."),
#     ("Pitrupaksha Begins","2027-09-16","#5d4037","Pitrupaksha Begins",
#      "May Pitrupaksha bring peace to departed souls and blessings to every family.",
#      "Wishing you a time of remembrance, gratitude and devotion.",
#      "May ancestral blessings bring strength, harmony and positivity.",
#      "Have a peaceful and blessed Pitrupaksha."),
#     ("Vishwakarma Puja","2027-09-17","#ff8f00","Happy Vishwakarma Puja",
#      "May Lord Vishwakarma bless every creator, craftsman and hardworking professional.",
#      "Wishing you success, creativity and prosperity in your work.",
#      "May your skills and efforts bring pride and happiness.",
#      "Have a blessed Vishwakarma Puja."),
#     ("Indira Ekadashi","2027-09-26","#1565c0","Happy Indira Ekadashi",
#      "May Lord Vishnu bless your family with peace, devotion and prosperity.",
#      "Wishing you strength, faith and positivity.",
#      "May your prayers bring divine grace and happiness.",
#      "Have a blessed Indira Ekadashi."),
#     ("Sarva Pitru Amavasya","2027-09-29","#4e342e","Sarva Pitru Amavasya",
#      "May the blessings of your ancestors bring peace and harmony to your family.",
#      "Wishing you a day of remembrance, gratitude and devotion.",
#      "May your prayers bring strength, serenity and family unity.",
#      "Have a peaceful Sarva Pitru Amavasya."),
#     ("Navratri","2027-09-30","#c2185b","Jai Mata Di",
#      "May Maa Durga bless you with strength, courage and happiness.",
#      "Celebrate nine nights of devotion, dance and divine energy.",
#      "May every day bring new hope, prosperity and positivity.",
#      "Have a blessed Navratri."),
#     ("Gandhi Jayanti","2027-10-02","#795548","Gandhi Jayanti",
#      "May the values of truth, peace and non-violence inspire us every day.",
#      "Wishing everyone harmony, kindness and positivity.",
#      "May unity and responsible citizenship strengthen our communities.",
#      "Happy Gandhi Jayanti."),
#     ("Saraswati Avahan","2027-10-06","#f4c430","Saraswati Avahan",
#      "May Goddess Saraswati bless you with wisdom, creativity and knowledge.",
#      "Wishing every learner and creator inspiration and confidence.",
#      "May the light of knowledge guide every step of your journey.",
#      "Have a blessed Saraswati Avahan."),
#     ("Saraswati Puja","2027-10-07","#f4c430","Happy Saraswati Puja",
#      "May Goddess Saraswati bless your life with wisdom and creativity.",
#      "Wishing you knowledge, learning and inspiration.",
#      "May your mind remain curious, focused and positive.",
#      "Have a blessed Saraswati Puja."),
#     ("Durga Ashtami","2027-10-07","#b71c1c","Jai Mata Di",
#      "May Maa Durga bless you with courage, strength and protection.",
#      "Wishing you peace, prosperity and divine energy.",
#      "May Shakti fill your heart with confidence.",
#      "Have a blessed Durga Ashtami."),
#     ("Maha Navami","2027-10-08","#d32f2f","Jai Mata Di",
#      "May Maa Durga bless your family with strength and divine grace.",
#      "Wishing you happiness, courage and prosperity.",
#      "May your life be filled with positive energy.",
#      "Have a blessed Maha Navami."),
#     ("Dussehra","2027-10-09","#ef6c00","Happy Dussehra",
#      "May truth, courage and positive actions always triumph in your life.",
#      "Wishing you success, happiness and strength.",
#      "May every obstacle be overcome with wisdom and determination.",
#      "Happy Dussehra!"),
#     ("Papankusha Ekadashi","2027-10-11","#1565c0","Happy Papankusha Ekadashi",
#      "May Lord Vishnu bless your life with peace and devotion.",
#      "Wishing you clarity, strength and positive energy.",
#      "May your prayers bring divine guidance.",
#      "Have a blessed Papankusha Ekadashi."),
#     ("Kojagara Puja","2027-10-14","#7b1fa2","Happy Kojagara Puja",
#      "May Goddess Lakshmi bless your home with prosperity and happiness.",
#      "Wishing your family abundance, peace and togetherness.",
#      "May every prayer bring new opportunities and positivity.",
#      "Have a blessed Kojagara Puja."),
#     ("Sharad Purnima","2027-10-14","#5e35b1","Happy Sharad Purnima",
#      "May the sacred full moon bring peace and positivity to your family.",
#      "Wishing you health, happiness and prosperity.",
#      "May this beautiful night fill your home with divine blessings.",
#      "Have a blessed Sharad Purnima."),
#     ("Karwa Chauth","2027-10-18","#ad1457","Happy Karwa Chauth",
#      "May love, trust and togetherness grow stronger every day.",
#      "Wishing couples happiness, health and beautiful memories.",
#      "May every family be blessed with love and prosperity.",
#      "Have a blessed Karwa Chauth."),
#     ("Ahoi Ashtami","2027-10-22","#8e24aa","Happy Ahoi Ashtami",
#      "May Ahoi Mata bless every family with happiness, health and protection.",
#      "Wishing children a bright future filled with love and success.",
#      "May your home always be filled with laughter and togetherness.",
#      "Have a blessed Ahoi Ashtami."),
#     ("Rama Ekadashi","2027-10-25","#1565c0","Happy Rama Ekadashi",
#      "May Lord Vishnu bless your family with peace, strength and prosperity.",
#      "Wishing you devotion, clarity and positive energy.",
#      "May your prayers bring happiness and divine guidance.",
#      "Have a blessed Rama Ekadashi."),
#     ("Govatsa Dwadashi","2027-10-26","#388e3c","Happy Govatsa Dwadashi",
#      "May this sacred day bring compassion, prosperity and harmony.",
#      "Wishing your family health, happiness and abundance.",
#      "May gratitude and kindness brighten every day.",
#      "Have a blessed Govatsa Dwadashi."),
#     ("Dhanteras","2027-10-27","#d4af37","Happy Dhanteras",
#      "May Goddess Lakshmi and Lord Dhanvantari bless your home with prosperity and health.",
#      "Wishing you wealth, happiness and success.",
#      "May this auspicious day bring abundance to your family.",
#      "Have a prosperous Dhanteras."),
#     ("Kali Chaudas","2027-10-27","#212121","Happy Kali Chaudas",
#      "May divine strength remove negativity and fear from your life.",
#      "Wishing you courage, peace and positive energy.",
#      "May your home remain protected and filled with light.",
#      "Have a blessed Kali Chaudas."),
#     ("Narak Chaturdashi","2027-10-28","#ff6f00","Happy Narak Chaturdashi",
#      "May all negativity disappear from your life.",
#      "Wishing you happiness, peace and positivity.",
#      "May divine light guide your path.",
#      "Have a blessed Narak Chaturdashi."),
#     ("Lakshmi Puja","2027-10-29","#d4af37","Happy Lakshmi Puja",
#      "May Goddess Lakshmi bless your home with wealth, peace and prosperity.",
#      "Wishing your family abundance, happiness and success.",
#      "May every diya bring hope and positivity.",
#      "Shubh Lakshmi Puja."),
#     ("Diwali","2027-10-29","#7a1738","Happy Diwali",
#      "May the festival of lights fill your home with happiness, love and prosperity.",
#      "Wishing you beautiful memories, success and togetherness.",
#      "May every diya brighten your path and every smile make your celebration special.",
#      "Shubh Deepavali!"),
#     ("Govardhan Puja","2027-10-30","#2e7d32","Happy Govardhan Puja",
#      "May Lord Krishna bless your family with prosperity, protection and happiness.",
#      "Wishing you abundance, gratitude and beautiful moments together.",
#      "May devotion and kindness always guide your path.",
#      "Have a blessed Govardhan Puja."),
#     ("Bhai Dooj","2027-10-31","#6a1b9a","Happy Bhai Dooj",
#      "May the beautiful bond between brothers and sisters remain strong forever.",
#      "Wishing your family love, laughter and togetherness.",
#      "May this special relationship bring endless happiness.",
#      "Happy Bhai Dooj!"),
#     ("Chhath Puja","2027-11-04","#e65100","Jai Chhathi Maiya",
#      "May Chhathi Maiya bless your family with health, prosperity and happiness.",
#      "Wishing you devotion, peace and strength.",
#      "May the rising Sun fill your life with hope and positive energy.",
#      "Have a blessed Chhath Puja."),
#     ("Kansa Vadh","2027-11-08","#5d4037","Kansa Vadh",
#      "May Lord Krishna inspire courage and righteousness in your life.",
#      "Wishing you strength to overcome negativity and challenges.",
#      "May truth, faith and devotion guide your family.",
#      "Have a blessed Kansa Vadh."),
#     ("Devutthana Ekadashi","2027-11-10","#1565c0","Happy Devutthana Ekadashi",
#      "May Lord Vishnu bless your home with peace, prosperity and devotion.",
#      "Wishing you fresh beginnings filled with hope and positivity.",
#      "May divine blessings guide every step of your journey.",
#      "Have a blessed Devutthana Ekadashi."),
#     ("Tulasi Vivah","2027-11-11","#388e3c","Happy Tulasi Vivah",
#      "May Tulsi Mata bless your home with peace, harmony and prosperity.",
#      "Wishing your family happiness and good fortune.",
#      "May devotion bring divine blessings into your life.",
#      "Have a blessed Tulasi Vivah."),
#     ("Kartika Purnima","2027-11-14","#5e35b1","Happy Kartika Purnima",
#      "May this sacred full moon bring peace, prosperity and divine blessings.",
#      "Wishing your family happiness, health and spiritual growth.",
#      "May your home shine with positivity and hope.",
#      "Have a blessed Kartika Purnima."),
#     ("Guru Nanak Jayanti","2027-11-14","#1565c0","Happy Gurpurab",
#      "May Guru Nanak Dev Ji's teachings inspire peace, compassion and humility.",
#      "Wishing you happiness, harmony and a life guided by truth.",
#      "May kindness and service always brighten your path.",
#      "Waheguru Ji Ka Khalsa, Waheguru Ji Ki Fateh!"),
#     ("Vrishchika Sankranti","2027-11-17","#ff9800","Happy Vrishchika Sankranti",
#      "May the Sun bring health, warmth and prosperity to your family.",
#      "Wishing you positive energy and successful beginnings.",
#      "May the season ahead bring growth and happiness.",
#      "Have a blessed Vrishchika Sankranti."),
#     ("Kalabhairav Jayanti","2027-11-20","#37474f","Jai Kalabhairav",
#      "May Lord Kalabhairav bless you with courage, protection and wisdom.",
#      "Wishing you strength to face every challenge with faith.",
#      "May your family remain surrounded by peace and divine grace.",
#      "Have a blessed Kalabhairav Jayanti."),
#     ("Utpanna Ekadashi","2027-11-24","#1565c0","Happy Utpanna Ekadashi",
#      "May Lord Vishnu bless your life with peace, devotion and wisdom.",
#      "Wishing you strength, clarity and positive thoughts.",
#      "May your sincere prayers bring divine grace.",
#      "Have a blessed Utpanna Ekadashi."),
#     ("Vivah Panchami","2027-12-03","#8e24aa","Happy Vivah Panchami",
#      "May the divine union of Shri Ram and Mata Sita inspire love and harmony.",
#      "Wishing your family peace, devotion and happiness.",
#      "May every relationship be blessed with understanding and respect.",
#      "Have a blessed Vivah Panchami."),
#     ("Gita Jayanti","2027-12-09","#8d6e63","Happy Gita Jayanti",
#      "May the wisdom of the Bhagavad Gita guide your thoughts and actions.",
#      "Wishing you courage, clarity and inner peace.",
#      "May every challenge become an opportunity to learn and grow.",
#      "Have a blessed Gita Jayanti."),
#     ("Mokshada Ekadashi","2027-12-09","#1565c0","Happy Mokshada Ekadashi",
#      "May Lord Vishnu bless your family with peace and spiritual strength.",
#      "Wishing you devotion, wisdom and positive thoughts.",
#      "May your prayers bring clarity and divine grace.",
#      "Have a blessed Mokshada Ekadashi."),
#     ("Dattatreya Jayanti","2027-12-13","#6a1b9a","Happy Dattatreya Jayanti",
#      "May Lord Dattatreya bless you with wisdom, peace and prosperity.",
#      "Wishing your family spiritual growth and happiness.",
#      "May divine guidance remain with you through every journey.",
#      "Have a blessed Dattatreya Jayanti."),
#     ("Margashirsha Purnima","2027-12-13","#5e35b1","Happy Margashirsha Purnima",
#      "May this sacred full moon bring peace, prosperity and divine blessings.",
#      "Wishing your family health, happiness and spiritual growth.",
#      "May your home remain filled with light and positivity.",
#      "Have a blessed Margashirsha Purnima."),
#     ("Dhanu Sankranti","2027-12-16","#ff9800","Happy Dhanu Sankranti",
#      "May the Sun bring warmth, health and prosperity to your family.",
#      "Wishing you positive energy and successful new beginnings.",
#      "May every day ahead be filled with hope and happiness.",
#      "Have a blessed Dhanu Sankranti."),
#     ("Saphala Ekadashi","2027-12-23","#1565c0","Happy Saphala Ekadashi",
#      "May Lord Vishnu bless your efforts with success and peace.",
#      "Wishing you strength, devotion and positive beginnings.",
#      "May your sincere efforts lead to beautiful results.",
#      "Have a blessed Saphala Ekadashi."),
#     ("Christmas","2027-12-25","#c62828","Merry Christmas",
#      "May Christmas fill your home with love, peace and happiness.",
#      "Wishing you beautiful moments with family and friends.",
#      "May the season bring hope, kindness and joyful new beginnings.",
#      "Merry Christmas."),
# ]

# rows = []
# slug_counts = {}
# trending = {
#     "Navratri","Dussehra","Diwali","Dhanteras","Bhai Dooj","Chhath Puja",
#     "Guru Nanak Jayanti","Christmas","Holi","Maha Shivaratri","Rama Navami",
#     "Hanuman Jayanti","Ganesh Chaturthi","Janmashtami","Raksha Bandhan",
#     "Ganesh Visarjan","Jagannath Rath Yatra","Makar Sankranti","Pongal",
#     "New Year"
# }

# import re
# def base_slug(name):
#     return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")

# for name, date, color, heading, m1, m2, m3, m4 in events:
#     year = int(date[:4])
#     b = base_slug(name)
#     slug_counts[b] = slug_counts.get(b, 0) + 1
#     slug = b if slug_counts[b] == 1 else f"{b}-{year}"
#     # Ensure repeated names in 2027 don't collide with an earlier 2026 slug.
#     if any(r["slug"] == slug for r in rows):
#         slug = f"{b}-{year}"
#     if any(r["slug"] == slug for r in rows):
#         slug = f"{b}-{year}-{slug_counts[b]}"
#     animation = "fireworks" if name in {"Diwali","Dhanteras","Holi","Maha Shivaratri","Hanuman Jayanti","Dussehra","Holika Dahan","Narak Chaturdashi","New Year","Republic Day"} else (
#         "confetti" if name in {"Navratri","Ganesh Chaturthi","Ganesh Visarjan","Raksha Bandhan","Bhai Dooj","Chhath Puja","Onam","Ugadi","Gudi Padwa","Pongal","Makar Sankranti"} else "glitter"
#     )
#     rows.append({
#         "name": name,
#         "slug": slug,
#         "date": f"{date} 00:00:00",
#         "heading": heading,
#         "message_1": m1,
#         "message_2": m2,
#         "message_3": m3,
#         "message_4": m4,
#         "theme_color": color,
#         "animation": animation,
#         "views": 0,
#         "is_trending": str(name in trending).lower(),
#         "is_active": "true",
#     })

# df = pd.DataFrame(rows, columns=columns)

# # Final safety checks
# assert df["slug"].is_unique
# assert not df.duplicated(subset=["name","date"]).any()
# assert df["date"].is_monotonic_increasing
# assert len(df) >= 100

# path = Path("/mnt/data/festival_import.csv")
# df.to_csv(path, index=False, encoding="utf-8-sig")

# print(f"Created: {path}")
# print(f"Total festivals: {len(df)}")
# print(f"2026 records: {(df['date'].str.startswith('2026')).sum()}")
# print(f"2027 records: {(df['date'].str.startswith('2027')).sum()}")
# print("Duplicate slugs:", df["slug"].duplicated().sum())
# print("Duplicate name/date pairs:", df.duplicated(subset=["name","date"]).sum())

# In a file named `factories.py` in your Django app's directory

import random
import factory
from faker import Faker
from django.contrib.auth.models import Group
from django.utils import timezone

from apps.account.models import Departement, Lecturer, Major, Student, User
from apps.pkm.admin import PKMActivity
from apps.pkm.models import PKMIdeaContribute, PKMProgram, PKMScheme
from apps.proposals.models import KeyStageAssesment1, SubmissionProposal, SubmissionsProposalApply
from apps.team.models import Team, TeamVacancies

fake = Faker()

categories_data = [
    ('PKM Riset Eksakta', 'PKM-RE'),
    ('PKM Riset Sosial Humaniora', 'PKM-RSH'),
    ('PKM Kewirausahaan', 'PKM-K'),
    ('PKM Pengabdian Kepada Masyarakat', 'PKM-PM'),
    ('PKM Penerapan Iptek', 'PKM-PI'),
    ('PKM Karsa Cipta', 'PKM-KC'),
    ('PKM Karya Inovatif', 'PKM-KI'),
    ('PKM Video Gagasan Konstruktif', 'PKM-VGK'),
    ('PKM Gagasan Futuristik Tertulis', 'PKM-GFT'),
    ('PKM Artikel Ilmiah', 'PKM-AI'),
]



groups_data = [
    'Guest',
    'Student',
    'Lecturer',
    'LecturerReviewer',
    'Admin'
]

key_penilaian_1 =[
'Kesalahan Ketidaksesuaian Isi Proposal Dengan Bidang Yang Diusulkan (Salah Bidang PKM) Kesalahan Judul (Akronim, Singkatan Tidak Baku atau Lebih Dari 20 Kata pada proposal)',
'Kesalahan Sampul (Terdapat Halaman Sampul/Cover)',
'Kesalahan Pengesahan (Terdapat Halaman Pengesahan)',
'Kesalahan Ukuran Kertas (Bukan A4)',
'Kesalahan Format Paragraf (Tidak Satu Kolom)',
'Kesalahan Font (Tidak Times New Roman, Ukuran 12)',
'Kesalahan Margin (Kiri Tidak 4cm, Atas, Kanan, Bawah Tidak 3cm)',
'Kesalahan Perataan Teks (Teks Paragraf Tidak Rata Kanan-Kiri)',
'Kesalahan Spasi (Teks Paragraf Tidak 1,15)',
'Kesalahan Abstrak',
'Terdapat Ringkasan',
'Kesalahan Sistematika Penulisan PKM',
'Kesalahan Nomor Halaman',
'Kesalahan Letak Nomor Halaman',
'Kesalahan Ketidaksesuaian Luaran Wajib (tidak harus urut) di Profil atau di proposal',
'Kesalahan Format Rekapitulasi Rencana Anggaran Biaya',
'Kesalahan Nominal Pengajuan Anggaran ke Dit. APTV/Belmawa (wajib min 6 jt dan maks 10 jt) Kesalahan Nominal Dana Pendamping Perguruan Tinggi (Min 500.000 dan Maks 2.000.000)',
'Kesalahan Format Jadwal Kegiatan (tidak Sesuai Lampiran 1 Buku Panduan)',
'Kesalahan Waktu Pelaksanaan (Tidak 3-4 Bulan)',
'Kesalahan Jumlah Halaman',
'Kesalahan Daftar Pustaka (Tidak Harvard Style, Urut Abjad, dan Menguraikan Nama Penulis)',
'Kesalahan Ketidaksesuaian Kelengkapan Dokumen dan Lampiran',
'Kesalahan Ketidaksesuaian Kriteria Keilmuan Bidang PKM atau Jumlah Anggota tidak Sesuai',
'Kesalahan Tanggal / Bulan / Tahun (Tidak antara 9 Februari - 10 Maret 2024)',
'Kesalahan Tanda Tangan (Pengusul / Pendamping / Mitra) Cropping Lokal Kesalahan Surat Pernyataan Ketua Tim Pengusul',
]


class KeyStageAssesment1Factory(factory.django.DjangoModelFactory):
    class Meta:
        model = KeyStageAssesment1

    title = factory.LazyAttribute(lambda x: x.title)

class SuperUserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user_{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    password = factory.PostGenerationMethodCall('set_password', 'password')
    is_staff = True
    is_superuser = True


class GroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Group

    name = factory.Iterator(groups_data)


departement_major_data = {
    'Departement Teknik Elektro': ['Teknik Elektronika', 'Telekomunikasi', 'Elektro Industri', 'Teknologi Rekaya Internet'],
    'Departement Teknik Informatika Dan Komputer': ['Teknik Informatika', 'Teknik Komputer', 'Data Science'],
    'Departement Teknik Mekanika Dan Energi': ['Teknik Mekatronika', 'Sistem Pembangkit Energi'],
    'Departement Teknologi Multimedia Kreatif': ['Teknologi Multimedia Broadcasting', 'Teknologi Game', 'Teknologi Rekayasa Multimedia']
}

class DepartmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Departement
        django_get_or_create = ('name',)

    name = factory.Iterator(departement_major_data.keys())

class MajorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Major
        django_get_or_create = ('name', 'department')

    # Removed the name attribute's previous method of generating names.

    department = factory.SubFactory(DepartmentFactory)

    @classmethod
    def create_batch(cls, **kwargs):
        for dept_name, majors in departement_major_data.items():
            department, _ = Departement.objects.get_or_create(name=dept_name)
            for major_name in majors:
                cls.create(name=major_name, department=department)

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    email = factory.LazyAttribute(lambda _: fake.email())
    username = factory.LazyAttribute(lambda _: fake.user_name())
    @factory.post_generation
    def groups(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            # A list of groups were passed in, use them
            for group_name in extracted:
                self.groups.add(Group.objects.get(name=group_name))

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """
        Override default _create method to set password to 'password' for all created users.
        """
        manager = cls._get_manager(model_class)
        # Bypass password validation by providing raw password
        return manager.create_user(*args, **kwargs, password='password')
    
    password = factory.PostGenerationMethodCall('set_password', '12345678ok')

class StudentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Student

    user = factory.SubFactory(UserFactory)
    full_name = factory.LazyAttribute(lambda _: fake.name())
    nrp = factory.LazyAttribute(lambda _: fake.random_number(digits=12))
    
    department = factory.LazyAttribute(
        lambda _: Departement.objects.get_or_create(
            name=random.choice(list(departement_major_data.keys()))
        )[0]
    )
    
    # Use a LazyAttribute to select a random major based on the department and create/get it
    major = factory.LazyAttribute(
        lambda o: Major.objects.get_or_create(
            name=random.choice(departement_major_data[o.department.name]),
            department=o.department
        )[0]
    )
    degree = factory.LazyAttribute(lambda _: fake.random_element(elements=(Student.DEGREE_CHOICES))[0])
    admission_year = factory.LazyAttribute(lambda _: fake.random_int(min=2019, max=2024))
    
class LecturerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Lecturer

    user = factory.SubFactory(UserFactory)
    full_name = factory.LazyAttribute(lambda _: fake.name())
    nidn = factory.LazyAttribute(lambda _: fake.random_number(digits=18))
    
    # Select a random department from departement_major_data
    department = factory.LazyAttribute(
        lambda _: Departement.objects.get_or_create(
            name=random.choice(list(departement_major_data.keys()))
        )[0]
    )

class TeamFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Team

    name = factory.Sequence(lambda n: f'Team {n}')
    description = factory.LazyAttribute(lambda _: fake.text())
    file_approvement_lecturer = factory.Maybe(
        factory.LazyAttribute(lambda _: bool(fake.random_int(min=0, max=1))),
        yes_declaration=factory.django.FileField(data=fake.text().encode(), filename=fake.file_name(extension="pdf")),
        no_declaration=None
    )
    leader = factory.SubFactory(StudentFactory)
    lecturer = factory.SubFactory(LecturerFactory)
    status = factory.Iterator(['ACTIVE', 'NOT_ACTIVE'])
    created_at = factory.LazyAttribute(lambda _: fake.date_time_this_year())
    updated_at = factory.LazyAttribute(lambda _: fake.date_time_this_year())

    @factory.post_generation
    def members(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            # A more flexible approach to adding members
            for member in extracted:
                self.members.add(member)

class TeamVacanciesFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TeamVacancies

    team = factory.SubFactory(TeamFactory)
    description = factory.Faker('paragraph')
    requirements = factory.LazyAttribute(lambda _: [fake.word() for _ in range(fake.random_int(min=1, max=5))])
    role = factory.Faker('job')
    created_at = factory.LazyAttribute(lambda _: fake.date_time_between(start_date="-1y", end_date="now", tzinfo=timezone.get_current_timezone()))
    closed_at = factory.LazyAttribute(lambda o: fake.date_time_between(start_date=o.created_at, end_date="+1y", tzinfo=timezone.get_current_timezone()))
    # Handling tags through a post-generation hook
    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for tag_name in extracted:
                tag, _ = Tag.objects.get_or_create(name=tag_name)
                self.tags.add(tag)



class PKMSchemeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PKMScheme
    name = factory.LazyAttribute(lambda _: fake.random_element(elements=categories_data)[0])
    abbreviation  = factory.LazyAttribute(lambda _: fake.random_element(elements=categories_data)[1])
    description = factory.LazyAttribute(lambda _: fake.text())


class PKMProgramFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PKMProgram

    name = factory.LazyAttribute(lambda _: f"PKM {fake.random_int(min=2000, max=2099)}")
    period = factory.LazyAttribute(lambda _: fake.random_int(min=2000, max=2099))
    due_time = factory.LazyAttribute(lambda _: fake.date_time_this_year(before_now=False, after_now=True, tzinfo=timezone.get_current_timezone()))
    
    @factory.post_generation
    def scheme(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for scheme in extracted:
                self.scheme.add(scheme)

class PKMActivityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PKMActivity
    program = factory.SubFactory(PKMProgramFactory)
    title = factory.Sequence(lambda n: f'Activity {n}')
    description = factory.LazyAttribute(lambda _: fake.text())
    due_time = factory.LazyAttribute(lambda _: fake.date_time_this_year(before_now=False, after_now=True, tzinfo=timezone.get_current_timezone()))


class ProposalIdeasContributorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PKMIdeaContribute
    
    title = factory.Sequence(lambda n: f'Proposal Idea {n}')
    description = factory.LazyAttribute(lambda _: fake.sentence(nb_words=10))
    problem = factory.LazyAttribute(lambda _: fake.sentence(nb_words=15))
    solution = factory.LazyAttribute(lambda _: fake.sentence(nb_words=20))
    user = factory.SubFactory(UserFactory)
    team = factory.SubFactory(TeamFactory, null=True)
    illustration = factory.django.ImageField(color='blue')
    file = factory.django.FileField(filename='test.txt')
    status = factory.Iterator(['SUBMITTED', 'ACCEPTED', 'REJECTED'])

# You may need to adjust this if you want to generate fake files

class SubmissionProposalFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SubmissionProposal

    program = factory.SubFactory(PKMProgramFactory)
    title = factory.Sequence(lambda n: f'Submission Proposal {n}')
    description = factory.LazyAttribute(lambda _: fake.sentence(nb_words=10))
    due_time = factory.LazyAttribute(lambda _: timezone.make_aware(fake.future_datetime()))
    addional_file = None  # You may need to adjust this if you want to generate fake files
    status = factory.LazyAttribute(lambda _: fake.random_element(['ARCHIVED', 'PUBLISHED']))

class SubmissionsProposalApplyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SubmissionsProposalApply

    submission = factory.SubFactory(SubmissionProposalFactory)
    category = None  # You may need to adjust this if you have a PKMSchemeFactory
    team = factory.SubFactory(TeamFactory)
    status = factory.LazyAttribute(lambda _: fake.random_element(['APPLIED', 'ACCEPTED', 'REJECTED']))
    team = factory.SubFactory(TeamFactory)
    lecturer = factory.SubFactory(LecturerFactory)
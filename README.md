# divar_tel_bot
a simple divar (divar.ir) script which collects house information and sends to telegram (using python, sqlalchemy, postgresql and telegram apis)
# requirements
install requirements from requirements.txt. you also need to create a python file named local_settings.py which contains a dictionary of database configurations (user, password, host, port and db)
# config
in config.json
set your bale bot api you got from @botfather
# your chat id
you can get the chat id you want the bot to send message to when you go to web.bale.ai
for example this chat is the main one https://web.bale.ai/chat/6425583673
and the id is 6425583673
add "a" between each chat id
# save file
set a save_file address with .csv
# not sent file
set a file address with .csv for saving data that was not sent due to problems
# romms
rooms can be 
'بدون اتاق'
'یک'
'دو'
'سه'
'چهار'
'بیشتر'
# proxies
set your proxys here

you can change the houseconfig for the app to find diffrent houses
# districts should be one or more of these
'آب جوار'
'آبیاری'
'آرامستان دارالرحمه'
'ابونصر'
'ابیوردی'
'احمدآباد'
'احمدی'
'ارم'
'اسحاق بیگ'
'اصلاح‌نژاد'
'اطلسی'
'امام حسین'
'بازار'
'باغ تخت'
'بالا کفت'
'بریجستون'
'بعثت'
'بنکداران'
'پارک آزادی'
'پانصد دستگاه (بلوار رحمت)'
'پای کتا'
'پردیس ارم'
'پودنک'
'تاچارا'
'تپه تلویزیون'
'تحولی'
'ترکان'
'ترمینال باربری'
'تل حسین‌آباد'
'تلخ داش'
'تندگویان'
'جانبازان'
'جمهوری'
'جوادیه'
'چغا'
'چنچنه'
'چو گیاه'
'حافظیه'
'حسین‌آباد'
'خلدبرین'
'خلیلی'
'دانشگاه شهید باهنر'
'دباغ خانه'
'درکی'
'دروازه اصفهان'
'دروازه کازرون'
'دست خضر'
'دشت چنار'
'دوکوهک'
'ده پیاله'
'دینکان'
'رحمت‌آباد'
'رضوان'
'رکن‌آباد'
'ریشمک'
'زرگری'
'زرهی'
'زند'
'زیباشهر'
'سامان'
'سایت اداری'
'ستارخان'
'سجاد (بنی هاشم)'
'سر باغ'
'سعدیه'
'سهل‌آباد'
'سیلو'
'سینما سعدی'
'شاه قلی بیگی'
'شریف‌آباد'
'شهر صدرا'
'شهرک آرین'
'شهرک امام حسین'
'شهرک امام رضا (فرگاز)'
'شهرک امیر کبیر'
'شهرک ایثار'
'شهرک باهنر'
'شهرک برق'
'شهرک بزین'
'شهرک بوتان'
'شهرک پردیس'
'شهرک پرواز'
'شهرک جماران'
'شهرک حجت‌آباد'
'شهرک دارائی'
'شهرک سجادیه'
'شهرک سراج'
'شهرک سعدی'
'شهرک شهید بهشتی'
'شهرک شهید مطهری'
'شهرک عرفان'
'شهرک فجر'
'شهرک قصر قمشه'
'شهرک کوشکک'
'شهرک گلستان'
'شهرک گلستان شمالی'
'شهرک گلها'
'شهرک مخابرات'
'شهرک مدرس'
'شهرک مهدی‌آباد'
'شهرک مهرگان'
'شهرک نصر'
'شهرک نواب صفوی'
'شهرک نیروی انتظامی'
'شهرک والفجر'
'شهرک ولیعصر'
'شهید بهنام امیری'
'شیخ علی چوپان'
'شیشه‌گری'
'صاحب الزمان'
'صاحب دیوان'
'عادل‌آباد (بلوار عدالت)'
'عفیف‌آباد'
'علی‌آباد'
'فرزانگان'
'فرهنگ شهر'
'فرهنگیان'
'فضل‌آباد'
'فضیلت'
'قدوسی شرقی'
'قدوسی غربی'
'قصرالدشت'
'قلعه شاهزاده بیگم'
'قلعه قبله'
'قلعه نو'
'کاراندیش'
'کفترک'
'کوزه‌گری'
'کوی آزادی'
'کوی زهرا'
'کوی فرهنگیان'
'کوی قضات'
'کوی ولیعصر'
'کوی یاس'
'کیان شهر'
'گلدشت'
'گلدشت حافظ'
'گلدشت محمدی'
'گلدشت معالی‌آباد'
'گلشن'
'گلکوب'
'گود عربان'
'گویم'
'لاله'
'لب آب'
'لشکری'
'ماه فیروزان'
'محراب'
'محله انجیر (کلبه)'
'محله سر دزک'
'محله سنگ سیاه'
'محله طلاب (نیستان)'
'محمدیه'
'محمودیه'
'مسلم'
'مشیر غربی'
'معالی‌آباد'
'مقر'
'ملاصدرا'
'منصورآباد'
'منطقه هوایی دوران'
'مهدی‌آباد'
'مهدیه'
'میانرود'
'میدان شاه'
'نارنجستان'
'نشاط'
'نصرآباد'
'نیایش'
'وحدت (بلوار مدرس)'
'وزیرآباد'
'وصال'
'ویلاشهر کیمیا'
'هفت تنان'
'هویزه'
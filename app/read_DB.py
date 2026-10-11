import psycopg
import arabic_reshaper
from bidi.algorithm import get_display

# تابع جادویی برای اصلاح حروف فارسی در ترمینال
def fix_persian(text):
    if text is None:
        text = "--- خالی ---"
    else:
        text = str(text)
    
    # چسباندن حروف به هم و تنظیم جهت راست‌به‌چپ
    reshaped_text = arabic_reshaper.reshape(text)
    return get_display(reshaped_text)

# لینک دیتابیس رانفلر
POSTGRES_URL = "postgresql://postgres:futOnc9vCcHYLp4wMR6l@remote-pishgaman.runflare.com:31589/habitodbhtr_db"

try:
    print(fix_persian("در حال اتصال به دیتابیس رانفلر...\n"))
    with psycopg.connect(POSTGRES_URL) as conn:
        with conn.cursor() as cur:
            # خواندن اطلاعات و مرتب‌سازی بر اساس تاریخ
            cur.execute("SELECT * FROM users ORDER BY id ASC;")
            rows = cur.fetchall()
            
            if not rows:
                print(fix_persian("جدول tasks در حال حاضر کاملاً خالی است."))
            else:
                print(fix_persian(f"✅ تعداد {len(rows)} تسک پیدا شد:\n"))
                
                # استخراج نام ستون‌ها
                col_names = [desc.name for desc in cur.description]
                
                # چاپ اطلاعات به صورت کارت‌های مرتب و تفکیک شده
                for i, row in enumerate(rows, 1):
                    print("=" * 50)
                    print(fix_persian(f"📌 رکورد ردیف {i}"))
                    print("=" * 50)
                    
                    # ترکیب نام ستون با مقدار آن
                    for col_name, value in zip(col_names, row):
                        
                        # اصلاح مقدار برای نمایش
                        display_value = fix_persian(value)
                        
                        # تراز کردن نام ستون‌ها (padding)
                        print(f"🔹 {col_name:<12} : {display_value}")
                    
                    print("\n")

except Exception as e:
    print(fix_persian(f"❌ خطا در خواندن اطلاعات از دیتابیس: {e}"))
from typing import Final, Dict
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, ContextTypes,  CallbackQueryHandler
import psycopg2
from psycopg2 import Error
from datetime import datetime
from decimal import Decimal

# Bot connection parameters
TOKEN:Final = "6039470513:AAEpKOCjc9laQ6bWcYuQNRyeC5q12CBM1iM"
BOT_USERNAME:Final = "@ecostore_robot"

# Database connection parameters
DB_USER = "root"
DB_PASSWORD = "RPY0mHYecwe7imLXRjE7MWfM"
DB_HOST = "ecodb"
DB_NAME = "postgres"
DB_PORT ="5432"

store_name = "اکو"
# Define a dictionary to keep track of conversation states for each user
conversation_states: Dict[int, str] = {}

# Define variables to store order information
link = ""
size = ""
color = ""
description = ""

# Define a dictionary for status codes and their Persian meanings
status_codes = {
    'P': 'در انتظار',
    'A': 'تایید شده',
    'C': 'پرداخت شده',
    'F': 'لغو شده',
    'S': 'ارسال شده',
    'R': 'دریافت شده'
}

## Command Handlers ##
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Connect to the PostgreSQL database
    conn = psycopg2.connect(user=DB_USER, password=DB_PASSWORD, host=DB_HOST, database=DB_NAME, port=DB_PORT)
    try:
        # Create a cursor object to execute SQL queries
        cursor = conn.cursor()
        
        # Extract user information
        user = update.message.from_user
        user_id = str(user.id)

        # Check if the user exists in the store_customer table
        cursor.execute("SELECT EXISTS(SELECT 1 FROM store_customer WHERE telegram_id = %s)", (user_id,))
        exists = cursor.fetchone()[0]
        
        if exists:
            # Fetch the user's name from the database
            cursor.execute("SELECT name FROM store_customer WHERE telegram_id = %s", (user_id,))
            saved_name = cursor.fetchone()[0]
            
            await update.message.reply_text(f"سلام {saved_name}! به آنلاین شاپ {store_name} خوش آمدید! 🍃")

            # Send menu with buttons
            keyboard = [[KeyboardButton("سفارش جدید 🛒"), KeyboardButton("سفارشات من 📋")],
                    [KeyboardButton("راهنمایی ℹ️"), KeyboardButton("کیف پول 💰")]]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
            await update.message.reply_text('لطفا انتخاب کنید:', reply_markup=reply_markup)
        else:
            # Request phone number from user
            contact_keyboard = KeyboardButton("ارسال شماره موبایل 📱", request_contact=True)
            custom_keyboard = [[contact_keyboard]]
            reply_markup = ReplyKeyboardMarkup(custom_keyboard)
            await update.message.reply_text(f"""
                                                سلام به آنلاین شاپ {store_name} خوش آمدید! 🍃 جهت شروع مراحل ثبت نام لظفا شماره موبایل خود را با استفاده از دکمه زیر ارسال کنید
                                            """, reply_markup=reply_markup)

    finally:
        # Close cursor and connection
        cursor.close()
        conn.close()

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        """
        /start : بازگشت به صفحه اصلی
        /help : استفاده از راهنمایی ربات
        """
    )
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if conversation_states.get(user_id) == 'add_funds':
        conn = psycopg2.connect(user=DB_USER, password=DB_PASSWORD, host=DB_HOST, database=DB_NAME, port=DB_PORT)
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM store_customer WHERE telegram_id = %s", (str(user_id),))
            customer_id = cursor.fetchone()[0]
            cursor.execute("SELECT id FROM store_wallet WHERE customer_id = %s", (customer_id,))
            wallet_id = cursor.fetchone()[0]
            
            if wallet_id:
                print(wallet_id)
                # Get file ID of the photo
                file_id = update.message.photo[-1].file_id
        
                # Download the photo
                file_path = await context.bot.get_file(file_id)
                file_extension = file_path.file_path.split('.')[-1]
        
                # Generate file name
                current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                file_name = f"{user_id}_receipt_{current_time}.{file_extension}"
                download_path = f"media/receipts/{file_name}"
                db_path = f"receipts/{file_name}"
        
                # Download and save the photo
                await file_path.download_to_drive(download_path)

                # Insert a new record into store_transaction
                cursor.execute("INSERT INTO store_transaction (action, amount, status, photo, wallet_id, created_at) VALUES (%s, %s, %s, %s, %s, NOW())",
                               ('D', 0, 'P', db_path, wallet_id))
                conn.commit()  # Commit the transaction

                # Send a confirmation message
                await update.message.reply_text('عکس رسید شما ثبت شد.')
            else:
                await update.message.reply_text('شما کیف پول ندارید جهت ساخت کیف پول روی دکمه کیف پول کلیک کنید.')
        finally:
            # Close cursor and connection
            cursor.close()
            conn.close()
        
        conversation_states[user_id] = None
    else:
        
        await update.message.reply_text('متاسفانه ارسال عکس فقط در بخش ارسال رسید مجاز است.')

async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.contact is not None:
        phone_number = update.message.contact.phone_number

        # Connect to the PostgreSQL database
        conn = psycopg2.connect(user=DB_USER, password=DB_PASSWORD, host=DB_HOST, database=DB_NAME, port=DB_PORT)
        try:
            # Create a cursor object to execute SQL queries
            cursor = conn.cursor()

            # Check if the user exists in the core_user table
            cursor.execute("SELECT id FROM core_user WHERE phone = %s", (phone_number,))
            user = cursor.fetchone()

            if user is None:
                # User does not exist, create a new user
                cursor.execute(
                    "INSERT INTO core_user (username, password, phone, is_active, date_joined, is_staff, is_superuser, email, first_name, last_name, otp) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id",
                    (phone_number, '', phone_number, True, datetime.now(), False, False, '', '',  '', '')
                )
                user_id = cursor.fetchone()[0]
                conn.commit()  # Commit the transaction
            else:
                # User exists, get the user id
                user_id = user[0]

            # Extract user information
            user = update.message.from_user
            telegram_id = str(user.id)
            name = f"{user.first_name} {user.last_name}" if user.last_name else user.first_name

            # Insert the new user into the store_customer table
            cursor.execute("INSERT INTO store_customer (name, telegram_id, user_id) VALUES (%s, %s, %s) RETURNING id", (name, telegram_id, user_id))
            customer_id = cursor.fetchone()[0]
            cursor.execute("INSERT INTO store_wallet (customer_id, amount) VALUES (%s, %s) RETURNING id",(customer_id, 0))
            conn.commit()  # Commit the transaction
            await update.message.reply_text(f'سلام به آنلاین شاپ {store_name} خوش آمدید! 🍃')

            # Send menu with buttons
            keyboard = [[KeyboardButton("سفارش جدید 🛒"), KeyboardButton("سفارشات من 📋")],
                    [KeyboardButton("راهنمایی ℹ️"), KeyboardButton("کیف پول 💰")]]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
            await update.message.reply_text('لطفا انتخاب کنید:', reply_markup=reply_markup)
        finally:
            # Close cursor and connection
            cursor.close()
            conn.close()


CONVERSATION_STATE = {}
def handle_response(text: str, user: str) -> str:
    message: str = text.lower()
    
    if "سفارش جدید 🛒" == message:
        CONVERSATION_STATE.clear()  # Clear previous conversation state
        CONVERSATION_STATE['step'] = 1

        
        return 'لینک سفارش خود را وارد کنید:'

    # Check current step of the conversation
    current_step = CONVERSATION_STATE.get('step')

    if 'بازگشت ↩️' == text:
        CONVERSATION_STATE.clear()
        return 1
    elif current_step == 1:
        CONVERSATION_STATE['link'] = text
        CONVERSATION_STATE['step'] = 2
        return 'سایز سفارش مورد نظر را وارد کنید:'

    elif current_step == 2:
        CONVERSATION_STATE['size'] = text
        CONVERSATION_STATE['step'] = 3
        return 'رنگ سفارش مورد نظر را وارد کنید:'

    elif current_step == 3:
        CONVERSATION_STATE['color'] = text
        CONVERSATION_STATE['step'] = 4
        return 'اگر توضیحاتی درمورد این سفارش دارید بنویسید:'

    elif current_step == 4:
        CONVERSATION_STATE['description'] = text
        
        # Establish connection to the PostgreSQL database
        try:
            conn = psycopg2.connect(user=DB_USER, password=DB_PASSWORD, host=DB_HOST, database=DB_NAME, port=DB_PORT)
            cursor = conn.cursor()

            cursor.execute("SELECT EXISTS(SELECT 1 FROM store_customer WHERE telegram_id = %s)", (str(user),))
            exists = cursor.fetchone()[0]

            if exists:
                # Fetch the user's name from the database
                cursor.execute("SELECT id FROM store_customer WHERE telegram_id = %s", (str(user),))
                customer_id = cursor.fetchone()[0]

                # Insert the order into the store_order table
                cursor.execute("INSERT INTO store_order (link, size, color, description, customer_id, created_at) VALUES (%s, %s, %s, %s, %s, NOW()) RETURNING id",
               (CONVERSATION_STATE['link'], CONVERSATION_STATE['size'], CONVERSATION_STATE['color'],
                CONVERSATION_STATE['description'], customer_id))

                order_id = cursor.fetchone()[0]

                cursor.execute("INSERT INTO store_orderstatus (status, status_change, order_id) VALUES (%s, %s, %s)",
                               ("P", datetime.now(), order_id))

            conn.commit()
            cursor.close()
            conn.close()
            
            # Generate response
            response = f"""
            لینک سفارش: {CONVERSATION_STATE['link']}
            سایز سفارش: {CONVERSATION_STATE['size']}
            رنگ سفارش: {CONVERSATION_STATE['color']}
            توضیحات: {CONVERSATION_STATE['description']}
            وضعیت سفارش: در حال انتظار
            """

            CONVERSATION_STATE.clear()  # Clear conversation state after completion
            return response

        except Error as e:
            print("Error while connecting to PostgreSQL", e)
            return  """
                        ببخشید، سفارش شما بدلیل مشکلاتی در سرور ثبت نشد.
                        لطفادوباره امتحان کنید. 🙏
                    """
    
    elif "راهنمایی ℹ️" == message:
        return """
        /start : بازگشت به صفحه اصلی
        /help : استفاده از راهنمایی ربات
        """
    elif "سفارشات من 📋" in message:
        return 0
    elif 'بازگشت ↩️' == message:
        return 1
    elif 'کیف پول 💰' in message:
        return 2
    else:
        return f"ببخشید، {message} در بین دستورات تعریف شده وجود ندارد."

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(update.message)
    text: str = update.message.text
    user: str = update.message.from_user.id
    print(f'user {update.message.chat.id}:  {text}')

    response: str = handle_response(text, user)
    print(response)
    if response == 1:
        keyboard = [[KeyboardButton("سفارش جدید 🛒"), KeyboardButton("سفارشات من 📋")],
                    [KeyboardButton("راهنمایی ℹ️"), KeyboardButton("کیف پول 💰")]]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
        await update.message.reply_text("بازگشت به صفحه اصلی", reply_markup=reply_markup)
    elif response == 0:
        user = str(update.message.from_user.id)
    
        try:
            # Establish connection to the PostgreSQL database
            conn = psycopg2.connect(user=DB_USER, password=DB_PASSWORD, host=DB_HOST, database=DB_NAME, port=DB_PORT)
            cursor = conn.cursor()

            cursor.execute("SELECT EXISTS(SELECT 1 FROM store_customer WHERE telegram_id = %s)", (str(user),))
            exists = cursor.fetchone()[0]

            if exists:
                # Fetch the user's name from the database
                cursor.execute("SELECT id FROM store_customer WHERE telegram_id = %s", (str(user),))
                customer_id = cursor.fetchone()[0]
                # Retrieve user's orders from the store_order table
                cursor.execute("SELECT id, description FROM store_order WHERE customer_id = %s", (customer_id,))
                orders = cursor.fetchall()
        
                if orders:
                    # Create a list of inline keyboard buttons for each order
                    keyboard = []
                    for order in orders:
                        # Check the latest status of the order
                        cursor.execute("""
                            SELECT status
                            FROM store_orderstatus
                            WHERE order_id = %s
                            ORDER BY status_change DESC
                            LIMIT 1
                        """, (order[0],))
                        latest_status = cursor.fetchone()
        
                        # Add a red X emoji to the order's name if the latest status is 'F'
                        order_name = ' ❌' + order[1] if latest_status and latest_status[0] == 'F' else order[1]
        
                        # Append the modified order name with the red X emoji to the keyboard
                        keyboard.append([InlineKeyboardButton(order_name, callback_data=f"order:{order[0]}")])


                    reply_markup = InlineKeyboardMarkup(keyboard)
                    await update.message.reply_text('لیست سفارشات شما:', reply_markup=reply_markup)
                else:
                    await update.message.reply_text('فعلا هیچ سفارشی ندارید')

        except Error as e:
            print("Error while connecting to PostgreSQL", e)
            await update.message.reply_text("ببخشید، مشکلی در نشان دادن لیست سفارشات داریم، لطفا دوباره امتحان کنید")

        finally:
            # Close cursor and connection
            cursor.close()
            conn.close()

    elif response == 2:
        user = str(update.message.from_user.id)

        try:
            # Establish connection to the PostgreSQL database
            conn = psycopg2.connect(user=DB_USER, password=DB_PASSWORD, host=DB_HOST, database=DB_NAME, port=DB_PORT)
            cursor = conn.cursor()

            cursor.execute("SELECT EXISTS(SELECT 1 FROM store_customer WHERE telegram_id = %s)", (str(user),))
            exists = cursor.fetchone()[0]

            if exists:
                # Fetch the user's id from the database
                cursor.execute("SELECT id FROM store_customer WHERE telegram_id = %s", (user,))
                customer_id = cursor.fetchone()[0]

                # Check if the user has a wallet
                cursor.execute("SELECT id, amount FROM store_wallet WHERE customer_id = %s", (customer_id,))
                wallet = cursor.fetchone()

                if wallet:
                    keyboard = [[InlineKeyboardButton(f"موجودی کیف پول: {wallet[1]} ريال", callback_data="check_balance")],
                        [InlineKeyboardButton("افزایش موجودی", callback_data="add_funds")]]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    await update.message.reply_text("💰 کیف پول شما:", reply_markup=reply_markup)

                else:
                    # If wallet does not exist, create a new one for the user
                    cursor.execute("INSERT INTO store_wallet (customer_id, amount) VALUES (%s, %s) RETURNING id",(customer_id, 0))
                    new_wallet = cursor.fetchone()[0]
                    conn.commit()
                    keyboard = [[InlineKeyboardButton(f"موجودی کیف پول: {new_wallet[1]}", callback_data="check_balance")],
                        [InlineKeyboardButton("افزایش موجودی", callback_data="add_funds")]]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    await update.message.reply_text("لطفا عملیات مورد نظر خود را انتخاب کنید:", reply_markup=reply_markup)

        except Error as e:
            print("Error while connecting to PostgreSQL", e)
            await update.message.reply_text("ببخشید، مشکلی در نشان دادن کیف پول داریم، لطفا دوباره امتحان کنید")

        finally:
            # Close cursor and connection
            cursor.close()
            conn.close()

    else:
        keyboard = [[KeyboardButton("بازگشت ↩️")]]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
        await update.message.reply_text(response, reply_markup=reply_markup)

async def handle_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    callback_data = query.data.split(":")
    
    if callback_data[0] == 'back_to_orders':
        user = str(query.from_user.id)
        try:
            # Establish connection to the PostgreSQL database
            conn = psycopg2.connect(user=DB_USER, password=DB_PASSWORD, host=DB_HOST, database=DB_NAME, port=DB_PORT)
            cursor = conn.cursor()

            cursor.execute("SELECT EXISTS(SELECT 1 FROM store_customer WHERE telegram_id = %s)", (str(user),))
            exists = cursor.fetchone()[0]

            if exists:
                # Fetch the user's name from the database
                cursor.execute("SELECT id FROM store_customer WHERE telegram_id = %s", (str(user),))
                customer_id = cursor.fetchone()[0]
                # Retrieve user's orders from the store_order table
                cursor.execute("SELECT id, description FROM store_order WHERE customer_id = %s", (customer_id,))
                orders = cursor.fetchall()
        
                if orders:
                    # Create a list of inline keyboard buttons for each order
                    keyboard = []
                    for order in orders:
                        # Check the latest status of the order
                        cursor.execute("""
                            SELECT status
                            FROM store_orderstatus
                            WHERE order_id = %s
                            ORDER BY status_change DESC
                            LIMIT 1
                        """, (order[0],))
                        latest_status = cursor.fetchone()
        
                        # Add a red X emoji to the order's name if the latest status is 'F'
                        order_name = ' ❌' + order[1] if latest_status and latest_status[0] == 'F' else order[1]
        
                        # Append the modified order name with the red X emoji to the keyboard
                        keyboard.append([InlineKeyboardButton(order_name, callback_data=f"order:{order[0]}")])

                    reply_markup = InlineKeyboardMarkup(keyboard)
                    await query.message.edit_text('لیست سفارشات شما:', reply_markup=reply_markup)
                else:
                    await query.message.edit_text('فعلا هیچ سفارشی ندارید')

        except Error as e:
            print("Error while connecting to PostgreSQL", e)
            await query.message.edit_text("ببخشید، مشکلی در نشان دادن لیست سفارشات داریم، لطفا دوباره امتحان کنید")

        finally:
            # Close cursor and connection
            cursor.close()
            conn.close()

    elif callback_data[0] == 'check_balance':
        user = str(query.from_user.id)

        try:
            # Establish connection to the PostgreSQL database
            conn = psycopg2.connect(user=DB_USER, password=DB_PASSWORD, host=DB_HOST, database=DB_NAME, port=DB_PORT)
            cursor = conn.cursor()

            cursor.execute("SELECT EXISTS(SELECT 1 FROM store_customer WHERE telegram_id = %s)", (str(user),))
            exists = cursor.fetchone()[0]

            if exists:
                # Fetch the user's id from the database
                cursor.execute("SELECT id FROM store_customer WHERE telegram_id = %s", (user,))
                customer_id = cursor.fetchone()[0]

                # Check if the user has a wallet
                cursor.execute("SELECT id, amount FROM store_wallet WHERE customer_id = %s", (customer_id,))
                wallet = cursor.fetchone()

                if wallet:
                    keyboard = [[InlineKeyboardButton(f"موجودی کیف پول: {wallet[1]} ريال", callback_data="check_balance")],
                        [InlineKeyboardButton("افزایش موجودی", callback_data="add_funds")]]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    await query.message.edit_text("💰 کیف پول شما:", reply_markup=reply_markup)

                else:
                    # If wallet does not exist, create a new one for the user
                    cursor.execute("INSERT INTO store_wallet (customer_id, amount) VALUES (%s, %s) RETURNING id",(customer_id, 0))
                    new_wallet = cursor.fetchone()[0]
                    conn.commit()
                    keyboard = [[InlineKeyboardButton(f"موجودی کیف پول: {new_wallet[1]}", callback_data="check_balance")],
                        [InlineKeyboardButton("افزایش موجودی", callback_data="add_funds")]]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    await query.message.edit_text("لطفا عملیات مورد نظر خود را انتخاب کنید:", reply_markup=reply_markup)

        except Error as e:
            print("Error while connecting to PostgreSQL", e)
            await query.message.edit_text("ببخشید، مشکلی در نشان دادن کیف پول داریم، لطفا دوباره امتحان کنید")

        finally:
            # Close cursor and connection
            cursor.close()
            conn.close()

    elif callback_data[0] == 'add_funds':
        conversation_states[query.from_user.id] = 'add_funds'
        await query.message.edit_text("لطفا میزان پولی که میخواهید به کیف پول خود اضافه کنید را به شماره حساب زیر واریز کنید و عکس رسید را ارسال کنید:\na fake شماره حساب for test")
    
    elif callback_data[0] == 'cancel_order':
        # Send a confirmation message with inline keyboard buttons
        keyboard = [
        [InlineKeyboardButton("بله 👍", callback_data=f"confirm_cancel:{callback_data[1]}")],
        [InlineKeyboardButton("خیر ✋", callback_data="back_to_orders")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.edit_text(
        "آیا میخواهید سفارش خود را لغو کنید؟",
        reply_markup=reply_markup
        )

    elif callback_data[0] == 'confirm_cancel':
        try:
            conn = psycopg2.connect(user=DB_USER, password=DB_PASSWORD, host=DB_HOST, database=DB_NAME, port=DB_PORT)
            cursor = conn.cursor()

            cursor.execute("INSERT INTO store_orderstatus (status, status_change, order_id) VALUES (%s, NOW(), %s)",
                               ("F", callback_data[1],))
            conn.commit()

            
            keyboard = [[InlineKeyboardButton("برگشت به سفارشات من 📋", callback_data="back_to_orders")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.message.edit_text("سفارش شما لغو شد.", reply_markup=reply_markup)

        except Error as e:
            print("Error while connecting to PostgreSQL", e)
            await query.message.edit_text("ببخشید، موقع دریافت اطلاعات به مشکل خوردیم. لطفا دوباره امتحان کنید.")

        finally:
            # Close cursor and connection
            cursor.close()
            conn.close()
    elif callback_data[0] == 'pay_order':
            user = str(query.from_user.id)
            try:
                # Fetch the user's id from the database
                conn = psycopg2.connect(user=DB_USER, password=DB_PASSWORD, host=DB_HOST, database=DB_NAME, port=DB_PORT)
                cursor = conn.cursor()

                cursor.execute("SELECT id FROM store_customer WHERE telegram_id = %s", (user,))
                customer_id = cursor.fetchone()[0]

                # Check if the user has a wallet
                cursor.execute("SELECT id, amount FROM store_wallet WHERE customer_id = %s", (customer_id,))
                wallet = cursor.fetchone()

                if wallet:
                    keyboard = [[InlineKeyboardButton(f"پرداخت از طریق کیف پول", callback_data=f"confirm_payment:{callback_data[1]}")],
                        [InlineKeyboardButton("افزایش موجودی", callback_data="add_funds")]]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    await query.message.edit_text(f"""
                                                موجودی کیف پول شما 💰: {wallet[1]}
                                                سفارش شما {callback_data[2]} تومان است.
                                                """, reply_markup=reply_markup)

                else:
                    # If wallet does not exist, create a new one for the user
                    cursor.execute("INSERT INTO store_wallet (customer_id, amount) VALUES (%s, %s) RETURNING id",(customer_id, 0))
                    new_wallet = cursor.fetchone()[0]
                    conn.commit()
                    keyboard = [[InlineKeyboardButton(f"پرداخت از طریق کیف پول", callback_data=f"confirm_payment:{callback_data[1]}")],
                        [InlineKeyboardButton("افزایش موجودی", callback_data="add_funds")]]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    await query.message.edit_text(f"""
                                                موجودی کیف پول شما 💰: {wallet[1]}
                                                سفارش شما {callback_data[2]} تومان است.
                                                """, reply_markup=reply_markup)
            except Error as e:
                print("Error while connecting to PostgreSQL", e)
                await query.message.edit_text("ببخشید، موقع دریافت اطلاعات به مشکل خوردیم. لطفا دوباره امتحان کنید.")

            finally:
                # Close cursor and connection
                cursor.close()
                conn.close()
    elif callback_data[0] == 'confirm_payment':
        user = str(query.from_user.id)
        try:
            # Fetch the user's id from the database
            conn = psycopg2.connect(user=DB_USER, password=DB_PASSWORD, host=DB_HOST, database=DB_NAME, port=DB_PORT)
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM store_customer WHERE telegram_id = %s", (user,))
            customer_id = cursor.fetchone()[0]

            # Check if the user has a wallet
            cursor.execute("SELECT id, amount FROM store_wallet WHERE customer_id = %s", (customer_id,))
            wallet = cursor.fetchone()

            cursor.execute("SELECT amount FROM store_orderinvoice WHERE order_id = %s AND status = %s", (callback_data[1],"P"))
            order_invoices = cursor.fetchall()
            total_amount = sum(amount[0] for amount in order_invoices)

            new_wallet = Decimal(wallet[1])-Decimal(total_amount)

            if new_wallet >= 0:
                cursor.execute("UPDATE store_wallet SET amount = %s WHERE id = %s", (str(new_wallet), wallet[0]))

                cursor.execute("UPDATE store_orderinvoice SET status = %s where order_id = %s", ("C", callback_data[1]))

                conn.commit()
                # Define the base keyboard with the 'back to orders' button
                keyboard = [[InlineKeyboardButton("برگشت به سفارشات من 📋", callback_data="back_to_orders")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                # Edit the original message with the order details and the button
                await query.message.edit_text("پرداخت موفقیت آمیز بود.", reply_markup=reply_markup)
            else:
                keyboard = [[InlineKeyboardButton("برگشت به سفارشات من 📋", callback_data="back_to_orders")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.message.edit_text("موجودی کیف پول شما کافی نیست. لطفا موجودی کیف پول خود را افزایش دهید.", reply_markup=reply_markup)

        except Error as e:
            print("Error while connecting to PostgreSQL", e)
            await query.message.edit_text("ببخشید، موقع دریافت اطلاعات به مشکل خوردیم. لطفا دوباره امتحان کنید.")

        finally:
            # Close cursor and connection
            cursor.close()
            conn.close()

    else:
        try:
            # Establish connection to the PostgreSQL database
            conn = psycopg2.connect(user=DB_USER, password=DB_PASSWORD, host=DB_HOST, database=DB_NAME, port=DB_PORT)
            cursor = conn.cursor()

            # Fetch the details of the selected order from the database
            cursor.execute("SELECT * FROM store_order WHERE id = %s", (callback_data[1],))
            order_details = cursor.fetchone()

            cursor.execute("SELECT * FROM store_orderstatus WHERE order_id = %s ORDER BY status_change DESC LIMIT 1;", (order_details[0],))
            order_status = cursor.fetchone()


            cursor.execute("SELECT amount FROM store_orderinvoice WHERE order_id = %s AND status = %s", (order_details[0],"P"))
            order_invoices = cursor.fetchall()
            # مجموع مبلغ‌ها را محاسبه کنید
            
            if order_details:
                # Assuming order_status[1] contains the status code
                status_text = status_codes.get(order_status[1], 'نامشخص')  # Default to 'نامشخص' if status code is not found
                total_amount = sum(amount[0] for amount in order_invoices)

                # Define the base keyboard with the 'back to orders' button
                keyboard = [[InlineKeyboardButton("برگشت به سفارشات من 📋", callback_data="back_to_orders")]]

                # Check if the order status is 'F'
                if order_status[1] == 'F':
                    order_message = f"""
                        لینک: {order_details[1]}
                        سایز: {order_details[2]}
                        رنگ: {order_details[3]}
                        توضیحات: {order_details[4]}
                        وضعیت سفارش: {status_text}
                        """
                else:
                    # نمایش مجموع مبلغ‌ها یا پیام "هنوز هزینه‌ای ثبت نشده است"
                    if total_amount:
                        if total_amount >= 0:
                            order_message = f"""
                            لینک: {order_details[1]}
                            سایز: {order_details[2]}
                            رنگ: {order_details[3]}
                            توضیحات: {order_details[4]}
                            وضعیت سفارش: {status_text}
                            مجموع هزینه ها: {total_amount}
                            """
                            # Add buttons for actions other than 'back to orders'
                            keyboard.extend([
                                [InlineKeyboardButton("لغو سفارش 🚫", callback_data=f"cancel_order:{callback_data[1]}")],
                                [InlineKeyboardButton("پرداخت سفارش 💳", callback_data=f"pay_order:{callback_data[1]}:{total_amount}")]
                            ])
                        else:
                            order_message = f"""
                            لینک: {order_details[1]}
                            سایز: {order_details[2]}
                            رنگ: {order_details[3]}
                            توضیحات: {order_details[4]}
                            وضعیت سفارش: {status_text}
                            مجموع هزینه های پرداخت نشده: {total_amount}
                            """
                    else:
                        order_message = f"""
                            لینک: {order_details[1]}
                            سایز: {order_details[2]}
                            رنگ: {order_details[3]}
                            توضیحات: {order_details[4]}
                            وضعیت سفارش: {status_text}
                            هنوز هزینه‌ای ثبت نشده است
                        """

                        keyboard.extend([
                            [InlineKeyboardButton("لغو سفارش 🚫", callback_data=f"cancel_order:{callback_data[1]}")]
                        ])

                reply_markup = InlineKeyboardMarkup(keyboard)
                # Edit the original message with the order details and the button
                await query.message.edit_text(order_message, reply_markup=reply_markup)
            else:
                await query.message.edit_text("ببخشید، این سفارش پیدا نشد.")

        except Error as e:
            print("Error while connecting to PostgreSQL", e)
            await query.message.edit_text("ببخشید، موقع دریافت اطلاعات به مشکل خوردیم. لطفا دوباره امتحان کنید.")

        finally:
            # Close cursor and connection
            cursor.close()
            conn.close()

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'update {update} caused error {context.error}')

from telegram import Bot

# Function to send a message via Telegram bot
def send_telegram_message(chat_id: int, text: str):
    """
    Sends a message to a user with the given chat_id using the Telegram bot.
    
    :param chat_id: Telegram user ID to whom the message will be sent.
    :param text: The message text to be sent.
    """
    print(f"sending message to {chat_id}")
    # Initialize the bot with your token
    bot = Bot(token=TOKEN)
    
    # Send the message
    bot.send_message(chat_id=chat_id, text=text)

if __name__ == '__main__':
    app  = Application.builder().token(TOKEN).build()

    ## Commands ##
    app.add_handler(CommandHandler("start", start_command))
    
    ## Messages ##
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.add_handler(MessageHandler(filters.CONTACT, handle_contact))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    ## Callbacks ##
    app.add_handler(CallbackQueryHandler(handle_callback))

    ## Errors ##
    app.add_error_handler(error)

    ## Polling ##
    print('Polling . . .')
    app.run_polling(allowed_updates=Update.ALL_TYPES)

                    

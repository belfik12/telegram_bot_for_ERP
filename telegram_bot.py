

"""
First, a few callback functions are defined. Then, those functions are passed to
the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line."""



import logging
import csv

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update,InlineKeyboardButton,InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
    CallbackContext,
    CallbackQueryHandler,
    
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

request_typ,driver_name, plate_number, milage, fuel_amt,fuel_typ,ent = range(7)
mnt_typ,mnt_dsc=range(2)

test=[]    #used to store driver and vehicle info 
driver_info=[]   #used to store data from the csv about specific driver that is analysed from test list
req_typ=''


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    
    
    keyboard = [
        [
            InlineKeyboardButton("Fuel request", callback_data='Fuel request'),
            InlineKeyboardButton("Maintenance request", callback_data='Maintenance request'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Hi! welcome to ERP bot,choose from fuel request or maintenance request",
    
        reply_markup=reply_markup
    )

    return request_typ

async def req(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    
    query=update.callback_query
    await query.answer()
    global req_typ
    req_typ=query.data
    test.append(query.data)     #Stores the request type
    logger.info("request type is %s",query.data)
    await query.edit_message_text(text="please enter the name of the driver",reply_markup=None,
    )
    return driver_name


async def driver(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the plate number of the vehicle."""
    user = update.message.from_user
    test.append(update.message.text)
    logger.info("driver name of %s: %s", user.first_name, update.message.text)
    await update.message.reply_text(
        "please enter plate number of the vehicle" ,
        reply_markup=ReplyKeyboardRemove(),
    )

    return plate_number


async def plate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the milage of the vehicle."""
    user = update.message.from_user
    test.append(update.message.text)
    logger.info("Plate number %s: %s", user.first_name,update.message.text)
    await update.message.reply_text(
        "enter milage of the vehicle."
    )

    return milage


async def mile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the fuel amount to be filled"""
    user = update.message.from_user
    test.append(update.message.text)
    logger.info("milage of  %s: %s.", user.first_name,update.message.text)
    if test[0]=='Fuel request':
        await update.message.reply_text(
        "enter fuel amount to be filled"
        )
        return fuel_amt
    else:
        keyboard = [
        [
            InlineKeyboardButton("Preventive maintenance", callback_data='General service'),
            InlineKeyboardButton("Breakdown maintenance", callback_data='Breakdown Maintenance'),
        ]
            ]
        reply_markup = InlineKeyboardMarkup(keyboard)
    
        await update.message.reply_text(
        "choose maintenance type",
        reply_markup=reply_markup
        )

        return fuel_amt

    
async def amount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    
    if test[0]=="Fuel request":
        """Stores the type of fuel to be filled"""
        test.append(update.message.text)
        logger.info(
            "fuel amount to be filed is %s",update.message.text
        )
        
        keyboard = [
            [
                InlineKeyboardButton("Benzene", callback_data='benz'),
                InlineKeyboardButton("Nafta", callback_data='nafta'),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("choose the fuel type", reply_markup=reply_markup)
        return fuel_typ
    else:
        query=update.callback_query
        await query.answer()
        test.append(query.data)
        await query.edit_message_text(text='enter maintenance description',reply_markup=None)
        return fuel_typ        


async def typ(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
   
    if test[0]=='Fuel request':
        query=update.callback_query
        await query.answer()
        test.append(query.data)
        logger.info("fuel type is  %s",query.data)
        d=''
        n=''
        keyboard=[
            [
                InlineKeyboardButton("Yes", callback_data='yes'),
                InlineKeyboardButton("No", callback_data='no'),
            ]
                ]
        reply_markup = InlineKeyboardMarkup(keyboard)
    
        with open('drivers_info.csv','r') as c:
            csv_reader=csv.reader(c)
            
            try:
                for drive in csv_reader:
                        
                    for i in drive[0][1:]:
                        
                        if d:
                            if i not in "aeiou" and d[-1]!=i:
                                d+=i
                        else:
                            if i not in "aeiou":
                                d+=i

                    for i in test[1][1:]:
                        
                        if n:
                            if i not in "aeiou" and n[-1]!=i:
                                n+=i
                        else:
                            if i not in "aeiou":
                                n+=i

                    first=(drive[0][0]+d).split(' ')[0]
                    first1=(test[1][0]+n).split(' ')[0]
                    if first.capitalize()==first1.capitalize():
                        global driver_info
                        driver_info=[test[2],drive[0],test[3],drive[2],drive[3],drive[1],test[4],test[5]]
                        await query.edit_message_text(text=f'is -{drive[0]}-correct?',reply_markup=reply_markup)
                        break

                        

                    n=""
                    d=""
            except Exception as e:
                print(str(e))
                pass            
        
        
        return ent 
    else:
        test.append(update.message.text)
        user=update.message.from_user
        logger.info("maintenance description entered by %s",user)
        d=''
        n=''

        keyboard=[
        [
            InlineKeyboardButton("Yes", callback_data='yes'),
            InlineKeyboardButton("No", callback_data='no'),
        ]
            ]
        reply_markup = InlineKeyboardMarkup(keyboard)
       
        with open('drivers_info.csv','r') as c:
            csv_reader=csv.reader(c)

            try:
                for drive in csv_reader:
                        
                    for i in drive[0][1:]:
                       
                        if d:
                            if i not in "aeiou" and d[-1]!=i:
                                d+=i
                        else:
                            if i not in "aeiou":
                                d+=i

                    for i in test[1][1:]:
                        
                        if n:
                            if i not in "aeiou" and n[-1]!=i:
                                n+=i
                        else:
                            if i not in "aeiou":
                                n+=i
                    
                    first=(drive[0][0]+d).split(' ')[0]
                    
                    first1=(test[1][0]+n).split(' ')[0]
                  
                    if first.capitalize()==first1.capitalize():
                
                        driver_info=[test[2],drive[0],test[3],drive[2],drive[3],drive[1],test[4],test[5]]
                        await update.message.reply_text(text=f'is -{drive[0]}-correct?',reply_markup=reply_markup)
                        
                        break


                    n=""
                    d=""
            except Exception as e:
                print(str(e))
                pass 
        return ent

async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) :
    #print(test)
    #print(driver_info)
    global req_typ
    global test
    #print(req_typ)
    
    try:
        if req_typ=='Fuel request':
            query=update.callback_query
            await query.answer()
            if query.data == 'yes':
                import fuel
                await query.edit_message_text(text='please wait a momment',reply_markup=None)
                global driver_info
                #print(driver_info)
                req_num=await fuel.fuel(driver_info,query)
                await query.edit_message_text(text=f'{req_num}:Open',reply_markup=None)
                #await update.message.reply_text(f'your request number is {req_num}',reply_markup=None)
                #global test
                test=[]
                driver_info=[]
            else:
                
                test=[]
                driver_info=[]
                
                
                await update.message.reply_text('the driver name is not correct please try again')
        else:
            query=update.callback_query
            await query.answer()
            if query.data == 'yes':
                import fuel
                await query.edit_message_text(text='please wait a momment',reply_markup=None)
                
                #global driver_info
                #print(driver_info)
                #await query.edit_message_text(text='almost there hang on',reply_markup=None)
                
                req_num=await fuel.maintenance(driver_info,query)
                await query.edit_message_text(text=f'{req_num}:Open',reply_markup=None)
                #global test
                test=[]
                driver_info=[]
            else:
                
                test=[]
                driver_info=[]
                
                
                await update.message.reply_text(text='the driver name is not correct please try again',reply_markup=None)
    
            
        return ConversationHandler.END
    except Exception as e:
        print(str(e))
        query=update.callback_query
        await query.answer()
        await query.edit_message_text(text='an error occured please try later',reply_markup=None)
        return ConversationHandler.END
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "Bye! ", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END

import time
from telegram.ext import Updater
from telegram import Bot
def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token("enter your telegram api token").read_timeout(300).write_timeout(300).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            
            request_typ: [CallbackQueryHandler(req)],
            driver_name: [MessageHandler(filters.TEXT, driver)],
            plate_number:[MessageHandler(filters.TEXT, plate)],
            milage: [MessageHandler(filters.TEXT, mile), CommandHandler("skip", milage)],
            fuel_amt: [
                MessageHandler(filters.TEXT, amount),CallbackQueryHandler(amount)],
            fuel_typ: [CallbackQueryHandler(typ),MessageHandler(filters.TEXT, typ)],
            #enter:[MessageHandler(filters.TEXT,dri)],
            ent:[CallbackQueryHandler(confirm)],
            
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    
    )
    
    application.add_handler(conv_handler)
    
    application.run_polling(allowed_updates=Update.ALL_TYPES,timeout=60)
    
if __name__ == "__main__":
    main()

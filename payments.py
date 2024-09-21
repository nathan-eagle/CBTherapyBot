import logging
from telegram import Update, LabeledPrice, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import add_credits, store_payment_id
from config import CREDIT_PACKAGES
from utils import get_main_menu_keyboard

logger = logging.getLogger(__name__)

async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    logger.debug(f"Buy function called for user {user_id}")

    keyboard = [
        [
            InlineKeyboardButton(
                f"💰 {package['credits']} Indecent Credits",
                callback_data=f"purchase_{package['credits']}_credits"
            )
        ]
        for package in CREDIT_PACKAGES.values()
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        await update.message.reply_text(
            "Select the number of Indecent Credits you want to purchase:",
            reply_markup=reply_markup
        )
        logger.debug(f"Sent credit package options to user {user_id}")
    except Exception as e:
        logger.error(f"Error sending credit package options to user {user_id}: {str(e)}")

async def process_purchase_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    data = query.data
    user_id = query.from_user.id

    try:
        credits = int(data.split('_')[1])
    except (IndexError, ValueError):
        await query.answer(text="Invalid selection.")
        logger.warning(f"User {user_id} made an invalid purchase selection: {data}")
        return

    if credits not in [package['credits'] for package in CREDIT_PACKAGES.values()]:
        await query.answer(text="Invalid credit package selected.")
        logger.warning(f"User {user_id} selected an invalid credit package: {credits}")
        return

    await query.answer()
    await send_invoice(update, context, credits)
    logger.debug(f"Processed purchase button for user {user_id}, credits: {credits}")

async def send_invoice(update: Update, context: ContextTypes.DEFAULT_TYPE, credits_needed: int) -> None:
    user_id = update.effective_user.id

    amount = credits_needed  # No need to multiply if using Telegram Stars

    prices = [
        LabeledPrice(label=f"{credits_needed} Indecent Credits", amount=amount)
    ]

    await context.bot.send_invoice(
        chat_id=user_id,
        title="Purchase Indecent Credits",
        description=f"Purchase {credits_needed} Indecent Credits.",
        payload=f"purchase_{credits_needed}_credits",
        provider_token="",  # Empty for Telegram Stars
        currency="XTR",     # Use "XTR" if you're using Telegram Stars
        prices=prices,
        start_parameter=f"purchase_{credits_needed}_credits",
    )
    logger.debug(f"Sent invoice to user {user_id} for {credits_needed} Indecent Credits.")

async def pre_checkout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.pre_checkout_query
    user_id = query.from_user.id
    total_amount = query.total_amount  # The amount in the smallest units (e.g., cents)

    try:
        payload_credits = int(query.invoice_payload.split('_')[1])
    except (IndexError, ValueError):
        await query.answer(ok=False, error_message="Invalid payment payload.")
        logger.warning(f"User {user_id} sent invalid payment payload: {query.invoice_payload}")
        return

    expected_amount = payload_credits  # Expected amount in smallest units

    if total_amount != expected_amount:
        await query.answer(ok=False, error_message="Incorrect payment amount.")
        logger.warning(f"User {user_id} has incorrect payment amount: {total_amount}, expected: {expected_amount}")
        return

    await query.answer(ok=True)
    logger.debug(f"Approved pre_checkout_query for user {user_id}.")

async def successful_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    payment = update.message.successful_payment
    user_id = update.effective_user.id
    logger.debug(f"Received successful payment from user {user_id}: {payment}")

    payload = payment.invoice_payload
    try:
        credits = int(payload.split('_')[1])
    except (IndexError, ValueError):
        logger.error(f"Invalid payload format: {payload}")
        await update.message.reply_text(
            "Payment was successful, but an error occurred while processing your purchase.",
            reply_markup=get_main_menu_keyboard()
        )
        return

    add_credits(user_id, credits)
    
    # Store the payment ID for potential refunds
    store_payment_id(user_id, payment.telegram_payment_charge_id, credits)

    confirmation_text = (
        f"Thank you for your purchase!\n"
        f"You have been credited with {credits} Indecent Credits.\n"
        #f"You have spent ${payment.total_amount / 100:.2f}."
    )
    await update.message.reply_text(confirmation_text, reply_markup=get_main_menu_keyboard())
    logger.debug(f"Successfully processed payment for user {user_id}. Added {credits} credits.")
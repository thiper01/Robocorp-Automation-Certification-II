import shutil

from robocorp import browser
from robocorp.tasks import task
from RPA.Archive import Archive
from RPA.HTTP import HTTP
from RPA.PDF import PDF
from RPA.Tables import Tables


@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    #Uncomment the line bellow for debug purposes
    #browser.configure(slowmo=200)
    open_robot_order_website()
    orders = get_orders()
    for order in orders:
        make_order(order)
    archive_receipts()
    clean_up()


def open_robot_order_website():
    """Opens the order website."""
    browser.goto("https://robotsparebinindustries.com/#/robot-order")


def get_orders():
    """Downloads the orders CSV and returns iterable table"""
    http = HTTP()
    http.download("https://robotsparebinindustries.com/orders.csv", overwrite=True)
    table = Tables()
    orders = table.read_table_from_csv("orders.csv")
    return orders


def make_order(order):
    """Inputs order info and clicks \"order\" """
    page = browser.page()
    head_names = {
        "1": "Roll-a-thor head",
        "2": "Peanut crusher head",
        "3": "D.A.V.E head",
        "4": "Andy Roid head",
        "5": "Spanner mate head",
        "6": "Drillbit 2000 head",
    }
    page.click("text=OK")
    head_number = order["Head"]
    page.select_option("#head", head_names.get(head_number))
    page.click('//*[@id="root"]/div/div[1]/div/div[1]/form/div[2]/div/div[{0}]/label'.format(order["Body"]))
    page.fill("input[placeholder='Enter the part number for the legs']", order["Legs"])
    page.fill("#address", order["Address"])
    while True:
        page.click("#order")
        if page.query_selector("#order-another"):
            break
    pdf = store_receipt_as_pdf(int(order["Order number"]))
    screenshot_path = screenshot_robot(int(order["Order number"]))
    embed_screenshot_to_receipt(screenshot_path, pdf)
    page.click("#order-another")


def store_receipt_as_pdf(order_number):
    """Save receipt as PDF"""
    page = browser.page()
    receipt_html = page.locator("#receipt").inner_html()
    pdf = PDF()
    pdf_path = "output/receipts/{0}.pdf".format(order_number)
    pdf.html_to_pdf(receipt_html, pdf_path)
    return pdf_path


def screenshot_robot(order_number):
    """Screenshots the robot"""
    page = browser.page()
    screenshot = "output/screenshots/{0}.png".format(order_number)
    page.locator("#robot-preview-image").screenshot(path=screenshot)
    return screenshot


def embed_screenshot_to_receipt(screenshot_path, pdf_file):
    """Embeds the screenshot to the receipt"""
    pdf = PDF()
    pdf.add_watermark_image_to_pdf(image_path=screenshot_path, source_path=pdf_file, output_path=pdf_file)


def archive_receipts():
    """Bundle zips pfds"""
    lib = Archive()
    lib.archive_folder_with_zip("./output/receipts", "./output/receipts.zip")


def clean_up():
    """Erases all unecessary files so there aren't too many artifacts"""
    shutil.rmtree("./output/receipts")
    shutil.rmtree("./output/screenshots")


# 📅 Laramie Events Calendar ICS/ICal Feed

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![ICS Feed](https://img.shields.io/badge/ICS%20Feed-Available-brightgreen)](https://chadjpetersen.github.io/laramie_events_calendar/events.ics)
[![Built with Python](https://img.shields.io/badge/Built%20With-Python-3776AB)](https://www.python.org/)

---

[Visit Laramie Events](https://www.visitlaramie.org/events/) is a great resource for finding things to do in Laramie.  
But I always forget to check it manually — I live by my calendar!  
So I thought it would be interesting to expose Laramie events as an **ICS feed**.

➡️ **ICS feed URL:** https://chadjpetersen.github.io/laramie_events_calendar/events.ics

You can subscribe to this feed with your favorite calendar app (Apple, Google, Microsoft, etc.) and have events show up automatically.

---

## 📥 How to Subscribe

- **Google Calendar**  
  [📖 Add an iCal URL to Google Calendar →](https://support.google.com/calendar/answer/37100?hl=en)  
  *(Use the "From URL" option and paste the ICS link. Scroll down to 'Use a link to add a public calendar' to find it.)*

- **Apple Calendar (Mac / iPhone)**  
  [📖 Subscribe to an iCal calendar in Apple Calendar →](https://support.apple.com/guide/calendar/subscribe-to-calendars-icl1022/mac)  
  *(On Mac: File > New Calendar Subscription... — On iPhone: Settings → Calendar → Accounts → Add Account → Other → Add Subscribed Calendar.)*

- **Microsoft Outlook**  
  [📖 Subscribe to an Internet Calendar in Outlook →](https://support.microsoft.com/en-us/office/import-or-subscribe-to-a-calendar-in-outlook-on-the-web-503ffaf6-7b86-44fe-8dd6-8099d95f38df)  
  *(Settings → Calendar → Shared Calendars → Add calendar → Subscribe from web.)*

---

## ⚙️ How It Works

- A Python script (`build_ics.py`) scrapes the latest events from Visit Laramie's website.
- It generates a `.ics` file.
- GitHub Actions automatically runs the script and publishes the file using GitHub Pages.

---

## 💬 Notes

- Events are scraped directly from publicly available listings.
- This project is unofficial and not affiliated with Visit Laramie. As such it may stop working at any moment.

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).

> Feel free to fork, modify, or reuse this project however you like!

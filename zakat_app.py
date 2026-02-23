#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
from datetime import datetime
from PIL import Image, ImageTk
import shutil

class ZakatManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Zakat Management System")
        self.root.geometry("1400x900")
        
        # Set up data directory in user's Documents
        self.data_dir = os.path.join(os.path.expanduser("~"), "Documents", "ZakatManagerData")
        self.photos_dir = os.path.join(self.data_dir, "photos")
        self.history_dir = os.path.join(self.data_dir, "history")
        self.ensure_directories()
        
        # Initialize data
        self.current_year = datetime.now().year
        self.data = self.load_data()
        
        
        # Currencies and settings
        self.currencies = ['USD', 'EUR', 'CNY', 'HKD', 'SGD', 'PKR', 'AED', 'SAR', 'GBP', 'JPY']
        self.zakat_rate = 2.5
        
        self.setup_ui()
        self.refresh_all()
    
    def ensure_directories(self):
        """Create necessary directories if they don't exist"""
        for dir_path in [self.data_dir, self.photos_dir, self.history_dir]:
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
                print(f"Created directory: {dir_path}")
    
    def get_data_file(self):
        return os.path.join(self.data_dir, f"zakat_data_{self.current_year}.json")
    
    def load_data(self):
        """Load data from JSON file"""
        data_file = self.get_data_file()
        if os.path.exists(data_file):
            with open(data_file, 'r') as f:
                return json.load(f)
        return self.get_default_data()
    
    def get_default_data(self):
        return {
            'members': [],
            'cash': [],
            'banks': [],
            'properties': [],
            'receivables': [],
            'gold': [],
            'recipients': [],
            'payments': [],
            'settings': {
                'zakat_rate': 2.5,
                'nisab': 150000,
                'gold_price_24k': 250000,
                'gold_price_22k': 229000,
                'gold_price_18k': 187500,
                'currency_rates': {
                    'USD': 280, 'EUR': 305, 'CNY': 39, 'HKD': 36,
                    'SGD': 208, 'PKR': 1, 'AED': 76, 'SAR': 75,
                    'GBP': 355, 'JPY': 1.9
                }
            }
        }
    
    def save_data(self):
        """Save data to JSON file"""
        data_file = self.get_data_file()
        with open(data_file, 'w') as f:
            json.dump(self.data, f, indent=2)
        print(f"Data saved to: {data_file}")
    
    def setup_ui(self):
        # Create notebook (tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create tabs
        self.dashboard_frame = ttk.Frame(self.notebook)
        self.members_frame = ttk.Frame(self.notebook)
        self.assets_frame = ttk.Frame(self.notebook)
        self.gold_frame = ttk.Frame(self.notebook)
        self.recipients_frame = ttk.Frame(self.notebook)
        self.payments_frame = ttk.Frame(self.notebook)
        self.settings_frame = ttk.Frame(self.notebook)
        self.history_frame = ttk.Frame(self.notebook)
        
        self.notebook.add(self.dashboard_frame, text='📊 Dashboard')
        self.notebook.add(self.members_frame, text='👥 Members')
        self.notebook.add(self.assets_frame, text='💰 Assets')
        self.notebook.add(self.gold_frame, text='🥇 Gold')
        self.notebook.add(self.recipients_frame, text='🤲 Recipients')
        self.notebook.add(self.payments_frame, text='💸 Payments')
        self.notebook.add(self.settings_frame, text='⚙️ Settings')
        self.notebook.add(self.history_frame, text='📜 History')
        
        self.setup_dashboard()
        self.setup_members()
        self.setup_assets()
        self.setup_gold()
        self.setup_recipients()
        self.setup_payments()
        self.setup_settings()
        self.setup_history()
    
    def setup_dashboard(self):
        # Year selector
        year_frame = ttk.Frame(self.dashboard_frame)
        year_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(year_frame, text="Year:", font=('Arial', 12, 'bold')).pack(side='left', padx=5)
        self.year_var = tk.StringVar(value=str(self.current_year))
        year_combo = ttk.Combobox(year_frame, textvariable=self.year_var, values=[str(y) for y in range(2020, 2030)], width=10)
        year_combo.pack(side='left', padx=5)
        year_combo.bind('<<ComboboxSelected>>', self.change_year)
        
        ttk.Button(year_frame, text="➕ New Year", command=self.create_new_year).pack(side='left', padx=5)
        ttk.Button(year_frame, text="💾 Backup", command=self.backup_data).pack(side='left', padx=5)
        ttk.Button(year_frame, text="📁 Open Data Folder", command=self.open_data_folder).pack(side='left', padx=5)
        
        # Stats frame
        stats_frame = ttk.LabelFrame(self.dashboard_frame, text="Zakat Summary", padding=10)
        stats_frame.pack(fill='x', padx=10, pady=5)
        
        self.total_zakat_label = ttk.Label(stats_frame, text="Total Zakat Due: 0 PKR", font=('Arial', 14, 'bold'))
        self.total_zakat_label.grid(row=0, column=0, padx=20, pady=5)
        
        self.total_paid_label = ttk.Label(stats_frame, text="Total Paid: 0 PKR", font=('Arial', 14, 'bold'))
        self.total_paid_label.grid(row=0, column=1, padx=20, pady=5)
        
        self.remaining_label = ttk.Label(stats_frame, text="Remaining: 0 PKR", font=('Arial', 14, 'bold'))
        self.remaining_label.grid(row=0, column=2, padx=20, pady=5)
        
        # Details notebook
        details_notebook = ttk.Notebook(self.dashboard_frame)
        details_notebook.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Currency breakdown
        currency_frame = ttk.Frame(details_notebook)
        details_notebook.add(currency_frame, text='Currency Breakdown')
        
        columns = ('Currency', 'Amount', 'Rate', 'PKR Value', 'Zakat (2.5%)')
        self.currency_tree = ttk.Treeview(currency_frame, columns=columns, show='headings')
        for col in columns:
            self.currency_tree.heading(col, text=col)
            self.currency_tree.column(col, width=120)
        self.currency_tree.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Gold summary
        gold_frame = ttk.Frame(details_notebook)
        details_notebook.add(gold_frame, text='Gold Summary')
        
        self.gold_summary_label = ttk.Label(gold_frame, text="No gold recorded", font=('Arial', 12))
        self.gold_summary_label.pack(padx=10, pady=10)
    
    def setup_members(self):
        # Toolbar
        toolbar = ttk.Frame(self.members_frame)
        toolbar.pack(fill='x', padx=5, pady=5)
        ttk.Button(toolbar, text="➕ Add Member", command=self.add_member_dialog).pack(side='left', padx=5)
        
        # Tree
        columns = ('Name', 'Mobile', 'NIC', 'Address', 'Photo')
        self.members_tree = ttk.Treeview(self.members_frame, columns=columns, show='headings')
        for col in columns:
            self.members_tree.heading(col, text=col)
            self.members_tree.column(col, width=150)
        self.members_tree.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self.members_tree, orient="vertical", command=self.members_tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.members_tree.configure(yscrollcommand=scrollbar.set)
        
        # Bind double click
        self.members_tree.bind('<Double-1>', self.edit_member)
    
    def setup_assets(self):
        # Notebook for asset types
        asset_notebook = ttk.Notebook(self.assets_frame)
        asset_notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Cash tab
        cash_frame = ttk.Frame(asset_notebook)
        asset_notebook.add(cash_frame, text='Cash')
        
        ttk.Button(cash_frame, text="➕ Add Cash", command=self.add_cash_dialog).pack(anchor='w', padx=5, pady=5)
        
        columns = ('Holder', 'Location', 'Currency', 'Amount', 'PKR Value')
        self.cash_tree = ttk.Treeview(cash_frame, columns=columns, show='headings')
        for col in columns:
            self.cash_tree.heading(col, text=col)
            self.cash_tree.column(col, width=120)
        self.cash_tree.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Banks tab
        banks_frame = ttk.Frame(asset_notebook)
        asset_notebook.add(banks_frame, text='Banks')
        
        ttk.Button(banks_frame, text="➕ Add Bank", command=self.add_bank_dialog).pack(anchor='w', padx=5, pady=5)
        
        columns = ('Bank', 'Account', 'Type', 'Currency', 'Balance', 'PKR Value')
        self.banks_tree = ttk.Treeview(banks_frame, columns=columns, show='headings')
        for col in columns:
            self.banks_tree.heading(col, text=col)
            self.banks_tree.column(col, width=100)
        self.banks_tree.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Property tab
        property_frame = ttk.Frame(asset_notebook)
        asset_notebook.add(property_frame, text='Property')
        
        ttk.Button(property_frame, text="➕ Add Property", command=self.add_property_dialog).pack(anchor='w', padx=5, pady=5)
        
        columns = ('Name', 'Type', 'Location', 'Value', 'For Trade', 'Zakat')
        self.property_tree = ttk.Treeview(property_frame, columns=columns, show='headings')
        for col in columns:
            self.property_tree.heading(col, text=col)
            self.property_tree.column(col, width=120)
        self.property_tree.pack(fill='both', expand=True, padx=5, pady=5)
    
    def setup_gold(self):
        toolbar = ttk.Frame(self.gold_frame)
        toolbar.pack(fill='x', padx=5, pady=5)
        ttk.Button(toolbar, text="➕ Add Gold", command=self.add_gold_dialog).pack(side='left', padx=5)
        
        # Price display
        self.gold_price_label = ttk.Label(toolbar, text="Gold Price: 24K: 0 | 22K: 0 | 18K: 0 PKR/Tola")
        self.gold_price_label.pack(side='left', padx=20)
        
        columns = ('Owner', 'Description', 'Weight (Tola)', 'Purity', 'Value (PKR)', 'Zakat')
        self.gold_tree = ttk.Treeview(self.gold_frame, columns=columns, show='headings')
        for col in columns:
            self.gold_tree.heading(col, text=col)
            self.gold_tree.column(col, width=120)
        self.gold_tree.pack(fill='both', expand=True, padx=5, pady=5)
    
    def setup_recipients(self):
        toolbar = ttk.Frame(self.recipients_frame)
        toolbar.pack(fill='x', padx=5, pady=5)
        ttk.Button(toolbar, text="➕ Add Recipient", command=self.add_recipient_dialog).pack(side='left', padx=5)
        
        columns = ('Name', 'Category', 'NIC', 'Mobile', 'Address', 'Total Received')
        self.recipients_tree = ttk.Treeview(self.recipients_frame, columns=columns, show='headings')
        for col in columns:
            self.recipients_tree.heading(col, text=col)
            self.recipients_tree.column(col, width=120)
        self.recipients_tree.pack(fill='both', expand=True, padx=5, pady=5)
    
    def setup_payments(self):
        toolbar = ttk.Frame(self.payments_frame)
        toolbar.pack(fill='x', padx=5, pady=5)
        ttk.Button(toolbar, text="➕ Make Payment", command=self.add_payment_dialog).pack(side='left', padx=5)
        
        self.available_funds_label = ttk.Label(toolbar, text="Available: 0 PKR", font=('Arial', 12, 'bold'))
        self.available_funds_label.pack(side='left', padx=20)
        
        columns = ('Date', 'Recipient', 'Amount (PKR)', 'Method', 'Notes')
        self.payments_tree = ttk.Treeview(self.payments_frame, columns=columns, show='headings')
        for col in columns:
            self.payments_tree.heading(col, text=col)
            self.payments_tree.column(col, width=150)
        self.payments_tree.pack(fill='both', expand=True, padx=5, pady=5)
    
    def setup_settings(self):
        frame = ttk.LabelFrame(self.settings_frame, text="Configuration", padding=20)
        frame.pack(fill='x', padx=10, pady=10)
        
        # Zakat rate
        ttk.Label(frame, text="Zakat Rate (%):").grid(row=0, column=0, sticky='w', pady=5)
        self.zakat_rate_entry = ttk.Entry(frame, width=10)
        self.zakat_rate_entry.insert(0, str(self.data['settings']['zakat_rate']))
        self.zakat_rate_entry.grid(row=0, column=1, sticky='w', padx=5)
        
        # Gold prices
        ttk.Label(frame, text="Gold Price 24K (PKR/Tola):").grid(row=1, column=0, sticky='w', pady=5)
        self.gold_24k_entry = ttk.Entry(frame, width=15)
        self.gold_24k_entry.insert(0, str(self.data['settings']['gold_price_24k']))
        self.gold_24k_entry.grid(row=1, column=1, sticky='w', padx=5)
        
        ttk.Label(frame, text="Gold Price 22K (PKR/Tola):").grid(row=2, column=0, sticky='w', pady=5)
        self.gold_22k_entry = ttk.Entry(frame, width=15)
        self.gold_22k_entry.insert(0, str(self.data['settings']['gold_price_22k']))
        self.gold_22k_entry.grid(row=2, column=1, sticky='w', padx=5)
        
        ttk.Label(frame, text="Gold Price 18K (PKR/Tola):").grid(row=3, column=0, sticky='w', pady=5)
        self.gold_18k_entry = ttk.Entry(frame, width=15)
        self.gold_18k_entry.insert(0, str(self.data['settings']['gold_price_18k']))
        self.gold_18k_entry.grid(row=3, column=1, sticky='w', padx=5)
        
        # Currency rates
        ttk.Label(frame, text="Currency Exchange Rates (to PKR):", font=('Arial', 10, 'bold')).grid(row=4, column=0, columnspan=2, sticky='w', pady=10)
        
        self.currency_entries = {}
        row = 5
        for curr in self.currencies:
            if curr != 'PKR':
                ttk.Label(frame, text=f"{curr}:").grid(row=row, column=0, sticky='w', pady=2)
                entry = ttk.Entry(frame, width=10)
                entry.insert(0, str(self.data['settings']['currency_rates'].get(curr, 1)))
                entry.grid(row=row, column=1, sticky='w', padx=5)
                self.currency_entries[curr] = entry
                row += 1
        
        ttk.Button(frame, text="💾 Save Settings", command=self.save_settings).grid(row=row, column=0, columnspan=2, pady=20)
        ttk.Button(frame, text="🗑️ Reset All Data", command=self.reset_all_data).grid(row=row+1, column=0, columnspan=2)
    
    def setup_history(self):
        toolbar = ttk.Frame(self.history_frame)
        toolbar.pack(fill='x', padx=5, pady=5)
        ttk.Button(toolbar, text="🔄 Refresh", command=self.refresh_history).pack(side='left', padx=5)
        
        columns = ('Year', 'Total Zakat', 'Total Paid', 'Remaining', 'Members', 'Recipients')
        self.history_tree = ttk.Treeview(self.history_frame, columns=columns, show='headings')
        for col in columns:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=120)
        self.history_tree.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.history_tree.bind('<Double-1>', self.restore_from_history)
    
    # Dialog methods
    def add_member_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Member")
        dialog.geometry("400x500")
        
        ttk.Label(dialog, text="Name:").pack(anchor='w', padx=5, pady=2)
        name_entry = ttk.Entry(dialog, width=40)
        name_entry.pack(fill='x', padx=5, pady=2)
        
        ttk.Label(dialog, text="Mobile:").pack(anchor='w', padx=5, pady=2)
        mobile_entry = ttk.Entry(dialog, width=40)
        mobile_entry.pack(fill='x', padx=5, pady=2)
        
        ttk.Label(dialog, text="NIC Number:").pack(anchor='w', padx=5, pady=2)
        nic_entry = ttk.Entry(dialog, width=40)
        nic_entry.pack(fill='x', padx=5, pady=2)
        
        ttk.Label(dialog, text="Address:").pack(anchor='w', padx=5, pady=2)
        address_entry = tk.Text(dialog, width=40, height=3)
        address_entry.pack(fill='x', padx=5, pady=2)
        
        photo_path = tk.StringVar()
        
        def select_photo():
            filename = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.jpeg *.png")])
            if filename:
                # Copy to photos directory
                ext = os.path.splitext(filename)[1]
                new_name = f"member_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
                new_path = os.path.join(self.photos_dir, new_name)
                shutil.copy(filename, new_path)
                photo_path.set(new_path)
                messagebox.showinfo("Success", "Photo saved!")
        
        ttk.Button(dialog, text="📷 Select Photo", command=select_photo).pack(anchor='w', padx=5, pady=5)
        
        def save():
            member = {
                'id': datetime.now().timestamp(),
                'name': name_entry.get(),
                'mobile': mobile_entry.get(),
                'nic': nic_entry.get(),
                'address': address_entry.get("1.0", "end-1c"),
                'photo': photo_path.get()
            }
            self.data['members'].append(member)
            self.save_data()
            self.refresh_members()
            dialog.destroy()
        
        ttk.Button(dialog, text="Save", command=save).pack(pady=20)
    
    def add_cash_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Cash")
        dialog.geometry("400x300")
        
        ttk.Label(dialog, text="Holder Name:").pack(anchor='w', padx=5)
        holder_entry = ttk.Entry(dialog, width=40)
        holder_entry.pack(fill='x', padx=5, pady=2)
        
        ttk.Label(dialog, text="Location:").pack(anchor='w', padx=5)
        location_entry = ttk.Entry(dialog, width=40)
        location_entry.pack(fill='x', padx=5, pady=2)
        
        ttk.Label(dialog, text="Currency:").pack(anchor='w', padx=5)
        currency_combo = ttk.Combobox(dialog, values=self.currencies, width=10)
        currency_combo.set('PKR')
        currency_combo.pack(anchor='w', padx=5, pady=2)
        
        ttk.Label(dialog, text="Amount:").pack(anchor='w', padx=5)
        amount_entry = ttk.Entry(dialog, width=20)
        amount_entry.pack(anchor='w', padx=5, pady=2)
        
        def save():
            cash = {
                'id': datetime.now().timestamp(),
                'holder': holder_entry.get(),
                'location': location_entry.get(),
                'currency': currency_combo.get(),
                'amount': float(amount_entry.get() or 0)
            }
            self.data['cash'].append(cash)
            self.save_data()
            self.refresh_assets()
            self.refresh_dashboard()
            dialog.destroy()
        
        ttk.Button(dialog, text="Save", command=save).pack(pady=20)
    
    def add_bank_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Bank Account")
        dialog.geometry("400x350")
        
        fields = ['Bank Name:', 'Account Number:', 'Account Type:', 'Currency:', 'Balance:']
        entries = []
        
        for field in fields:
            ttk.Label(dialog, text=field).pack(anchor='w', padx=5)
            if field == 'Account Type:':
                entry = ttk.Combobox(dialog, values=['Savings', 'Current', 'Fixed Deposit'], width=20)
                entry.set('Savings')
            elif field == 'Currency:':
                entry = ttk.Combobox(dialog, values=self.currencies, width=10)
                entry.set('PKR')
            else:
                entry = ttk.Entry(dialog, width=40)
            entry.pack(fill='x', padx=5, pady=2)
            entries.append(entry)
        
        def save():
            bank = {
                'id': datetime.now().timestamp(),
                'name': entries[0].get(),
                'account': entries[1].get(),
                'type': entries[2].get(),
                'currency': entries[3].get(),
                'balance': float(entries[4].get() or 0)
            }
            self.data['banks'].append(bank)
            self.save_data()
            self.refresh_assets()
            self.refresh_dashboard()
            dialog.destroy()
        
        ttk.Button(dialog, text="Save", command=save).pack(pady=20)
    
    def add_property_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Property")
        dialog.geometry("400x350")
        
        ttk.Label(dialog, text="Property Name:").pack(anchor='w', padx=5)
        name_entry = ttk.Entry(dialog, width=40)
        name_entry.pack(fill='x', padx=5, pady=2)
        
        ttk.Label(dialog, text="Type:").pack(anchor='w', padx=5)
        type_combo = ttk.Combobox(dialog, values=['Residential', 'Commercial', 'Land', 'Rental'], width=20)
        type_combo.set('Residential')
        type_combo.pack(anchor='w', padx=5, pady=2)
        
        ttk.Label(dialog, text="Location:").pack(anchor='w', padx=5)
        location_entry = ttk.Entry(dialog, width=40)
        location_entry.pack(fill='x', padx=5, pady=2)
        
        ttk.Label(dialog, text="Value (PKR):").pack(anchor='w', padx=5)
        value_entry = ttk.Entry(dialog, width=20)
        value_entry.pack(anchor='w', padx=5, pady=2)
        
        ttk.Label(dialog, text="For Trade/Business?").pack(anchor='w', padx=5)
        trade_var = tk.StringVar(value='no')
        ttk.Radiobutton(dialog, text="Yes (Zakat applicable)", variable=trade_var, value='yes').pack(anchor='w', padx=5)
        ttk.Radiobutton(dialog, text="No (Personal use - exempt)", variable=trade_var, value='no').pack(anchor='w', padx=5)
        
        def save():
            prop = {
                'id': datetime.now().timestamp(),
                'name': name_entry.get(),
                'type': type_combo.get(),
                'location': location_entry.get(),
                'value': float(value_entry.get() or 0),
                'for_trade': trade_var.get()
            }
            self.data['properties'].append(prop)
            self.save_data()
            self.refresh_assets()
            self.refresh_dashboard()
            dialog.destroy()
        
        ttk.Button(dialog, text="Save", command=save).pack(pady=20)
    
    def add_gold_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Gold")
        dialog.geometry("400x300")
        
        ttk.Label(dialog, text="Owner Name:").pack(anchor='w', padx=5)
        owner_entry = ttk.Entry(dialog, width=40)
        owner_entry.pack(fill='x', padx=5, pady=2)
        
        ttk.Label(dialog, text="Description:").pack(anchor='w', padx=5)
        desc_entry = ttk.Entry(dialog, width=40)
        desc_entry.pack(fill='x', padx=5, pady=2)
        
        ttk.Label(dialog, text="Weight (Tola):").pack(anchor='w', padx=5)
        weight_entry = ttk.Entry(dialog, width=20)
        weight_entry.pack(anchor='w', padx=5, pady=2)
        
        ttk.Label(dialog, text="Purity:").pack(anchor='w', padx=5)
        purity_combo = ttk.Combobox(dialog, values=['24', '22', '18'], width=10)
        purity_combo.set('24')
        purity_combo.pack(anchor='w', padx=5, pady=2)
        
        def save():
            gold = {
                'id': datetime.now().timestamp(),
                'owner': owner_entry.get(),
                'description': desc_entry.get(),
                'weight': float(weight_entry.get() or 0),
                'purity': purity_combo.get()
            }
            self.data['gold'].append(gold)
            self.save_data()
            self.refresh_gold()
            self.refresh_dashboard()
            dialog.destroy()
        
        ttk.Button(dialog, text="Save", command=save).pack(pady=20)
    
    def add_recipient_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Recipient")
        dialog.geometry("400x550")
        
        ttk.Label(dialog, text="Name:").pack(anchor='w', padx=5)
        name_entry = ttk.Entry(dialog, width=40)
        name_entry.pack(fill='x', padx=5, pady=2)
        
        ttk.Label(dialog, text="Category:").pack(anchor='w', padx=5)
        category_combo = ttk.Combobox(dialog, values=[
            'Poor (Fuqara)', 'Needy (Masakin)', 'Zakat Collector (Amil)',
            'New Muslim (Muallaf)', 'Freeing Slaves (Riqab)', 'Debtor (Gharim)',
            'Cause of Allah (Fi Sabilillah)', 'Wayfarer (Ibn Sabil)'
        ], width=30)
        category_combo.set('Poor (Fuqara)')
        category_combo.pack(anchor='w', padx=5, pady=2)
        
        ttk.Label(dialog, text="NIC Number:").pack(anchor='w', padx=5)
        nic_entry = ttk.Entry(dialog, width=40)
        nic_entry.pack(fill='x', padx=5, pady=2)
        
        ttk.Label(dialog, text="Mobile:").pack(anchor='w', padx=5)
        mobile_entry = ttk.Entry(dialog, width=40)
        mobile_entry.pack(fill='x', padx=5, pady=2)
        
        ttk.Label(dialog, text="Address:").pack(anchor='w', padx=5)
        address_entry = tk.Text(dialog, width=40, height=3)
        address_entry.pack(fill='x', padx=5, pady=2)
        
        photo_path = tk.StringVar()
        nic_photo_path = tk.StringVar()
        
        def select_photo(type):
            filename = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.jpeg *.png")])
            if filename:
                ext = os.path.splitext(filename)[1]
                prefix = "recipient_" if type == "photo" else "recipient_nic_"
                new_name = f"{prefix}{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
                new_path = os.path.join(self.photos_dir, new_name)
                shutil.copy(filename, new_path)
                if type == "photo":
                    photo_path.set(new_path)
                else:
                    nic_photo_path.set(new_path)
                messagebox.showinfo("Success", f"{type.title()} saved!")
        
        ttk.Button(dialog, text="📷 Select Photo", command=lambda: select_photo("photo")).pack(anchor='w', padx=5, pady=5)
        ttk.Button(dialog, text="🆔 Select NIC Photo", command=lambda: select_photo("nic")).pack(anchor='w', padx=5, pady=5)
        
        def save():
            recipient = {
                'id': datetime.now().timestamp(),
                'name': name_entry.get(),
                'category': category_combo.get(),
                'nic': nic_entry.get(),
                'mobile': mobile_entry.get(),
                'address': address_entry.get("1.0", "end-1c"),
                'photo': photo_path.get(),
                'nic_photo': nic_photo_path.get()
            }
            self.data['recipients'].append(recipient)
            self.save_data()
            self.refresh_recipients()
            dialog.destroy()
        
        ttk.Button(dialog, text="Save", command=save).pack(pady=20)
    
    def add_payment_dialog(self):
        if not self.data['recipients']:
            messagebox.showwarning("Warning", "Please add recipients first!")
            return
        
        available = self.calculate_total_zakat() - self.calculate_total_paid()
        if available <= 0:
            messagebox.showwarning("Warning", "No available Zakat funds!")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Make Payment")
        dialog.geometry("400x350")
        
        ttk.Label(dialog, text=f"Available: {available:,.2f} PKR", font=('Arial', 12, 'bold')).pack(pady=5)
        
        ttk.Label(dialog, text="Recipient:").pack(anchor='w', padx=5)
        recipient_combo = ttk.Combobox(dialog, values=[r['name'] for r in self.data['recipients']], width=30)
        recipient_combo.pack(fill='x', padx=5, pady=2)
        
        ttk.Label(dialog, text="Amount (PKR):").pack(anchor='w', padx=5)
        amount_entry = ttk.Entry(dialog, width=20)
        amount_entry.pack(anchor='w', padx=5, pady=2)
        
        ttk.Label(dialog, text="Payment Method:").pack(anchor='w', padx=5)
        method_combo = ttk.Combobox(dialog, values=['Cash', 'Bank Transfer', 'Mobile Wallet', 'Check'], width=20)
        method_combo.set('Cash')
        method_combo.pack(anchor='w', padx=5, pady=2)
        
        ttk.Label(dialog, text="Date:").pack(anchor='w', padx=5)
        date_entry = ttk.Entry(dialog, width=20)
        date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
        date_entry.pack(anchor='w', padx=5, pady=2)
        
        ttk.Label(dialog, text="Notes:").pack(anchor='w', padx=5)
        notes_entry = tk.Text(dialog, width=40, height=3)
        notes_entry.pack(fill='x', padx=5, pady=2)
        
        def save():
            amount = float(amount_entry.get() or 0)
            if amount > available:
                messagebox.showerror("Error", "Amount exceeds available funds!")
                return
            
            recipient = next((r for r in self.data['recipients'] if r['name'] == recipient_combo.get()), None)
            if not recipient:
                messagebox.showerror("Error", "Please select a recipient!")
                return
            
            payment = {
                'id': datetime.now().timestamp(),
                'recipient_id': recipient['id'],
                'amount': amount,
                'method': method_combo.get(),
                'date': date_entry.get(),
                'notes': notes_entry.get("1.0", "end-1c")
            }
            self.data['payments'].append(payment)
            self.save_data()
            self.refresh_payments()
            self.refresh_dashboard()
            self.refresh_recipients()
            dialog.destroy()
        
        ttk.Button(dialog, text="Make Payment", command=save).pack(pady=20)
    
    # Calculation methods
    def calculate_total_zakat(self):
        total = 0
        
        # Cash
        for cash in self.data['cash']:
            rate = self.data['settings']['currency_rates'].get(cash['currency'], 1)
            total += cash['amount'] * rate
        
        # Banks
        for bank in self.data['banks']:
            rate = self.data['settings']['currency_rates'].get(bank['currency'], 1)
            total += bank['balance'] * rate
        
        # Receivables
        for rec in self.data['receivables']:
            rate = self.data['settings']['currency_rates'].get(rec['currency'], 1)
            total += rec['amount'] * rate
        
        # Gold
        for gold in self.data['gold']:
            if gold['purity'] == '24':
                price = self.data['settings']['gold_price_24k']
            elif gold['purity'] == '22':
                price = self.data['settings']['gold_price_22k']
            else:
                price = self.data['settings']['gold_price_18k']
            total += gold['weight'] * price
        
        # Property (trade only)
        for prop in self.data['properties']:
            if prop.get('for_trade') == 'yes':
                total += prop['value']
        
        return total * (self.data['settings']['zakat_rate'] / 100)
    
    def calculate_total_paid(self):
        return sum(p['amount'] for p in self.data['payments'])
    
    # Refresh methods
    def refresh_all(self):
        self.refresh_dashboard()
        self.refresh_members()
        self.refresh_assets()
        self.refresh_gold()
        self.refresh_recipients()
        self.refresh_payments()
        self.refresh_history()
    
    def refresh_dashboard(self):
        total_zakat = self.calculate_total_zakat()
        total_paid = self.calculate_total_paid()
        remaining = total_zakat - total_paid
        
        self.total_zakat_label.config(text=f"Total Zakat Due: {total_zakat:,.2f} PKR")
        self.total_paid_label.config(text=f"Total Paid: {total_paid:,.2f} PKR")
        self.remaining_label.config(text=f"Remaining: {remaining:,.2f} PKR")
        
        # Currency breakdown
        for item in self.currency_tree.get_children():
            self.currency_tree.delete(item)
        
        currency_totals = {}
        for c in self.currencies:
            currency_totals[c] = 0
        
        for cash in self.data['cash']:
            currency_totals[cash['currency']] += cash['amount']
        for bank in self.data['banks']:
            currency_totals[bank['currency']] += bank['balance']
        for rec in self.data['receivables']:
            currency_totals[rec['currency']] += rec['amount']
        
        for curr, amount in currency_totals.items():
            if amount > 0:
                rate = self.data['settings']['currency_rates'].get(curr, 1)
                pkr_value = amount * rate
                zakat = pkr_value * (self.data['settings']['zakat_rate'] / 100)
                self.currency_tree.insert('', 'end', values=(
                    curr, f"{amount:,.2f}", rate, f"{pkr_value:,.2f}", f"{zakat:,.2f}"
                ))
        
        # Gold summary
        total_weight = sum(g['weight'] for g in self.data['gold'])
        total_gold_value = 0
        for g in self.data['gold']:
            if g['purity'] == '24':
                price = self.data['settings']['gold_price_24k']
            elif g['purity'] == '22':
                price = self.data['settings']['gold_price_22k']
            else:
                price = self.data['settings']['gold_price_18k']
            total_gold_value += g['weight'] * price
        
        self.gold_summary_label.config(text=f"Total: {total_weight:.2f} Tola | Value: {total_gold_value:,.2f} PKR | Zakat: {total_gold_value * 0.025:,.2f} PKR")
    
    def refresh_members(self):
        for item in self.members_tree.get_children():
            self.members_tree.delete(item)
        for member in self.data['members']:
            self.members_tree.insert('', 'end', values=(
                member['name'], member['mobile'], member['nic'], 
                member['address'][:30] + '...' if len(member['address']) > 30 else member['address'],
                'Yes' if member.get('photo') else 'No'
            ))
    
    def refresh_assets(self):
        # Cash
        for item in self.cash_tree.get_children():
            self.cash_tree.delete(item)
        for cash in self.data['cash']:
            rate = self.data['settings']['currency_rates'].get(cash['currency'], 1)
            pkr = cash['amount'] * rate
            self.cash_tree.insert('', 'end', values=(
                cash['holder'], cash['location'], cash['currency'], 
                f"{cash['amount']:,.2f}", f"{pkr:,.2f}"
            ))
        
        # Banks
        for item in self.banks_tree.get_children():
            self.banks_tree.delete(item)
        for bank in self.data['banks']:
            rate = self.data['settings']['currency_rates'].get(bank['currency'], 1)
            pkr = bank['balance'] * rate
            self.banks_tree.insert('', 'end', values=(
                bank['name'], bank['account'], bank['type'], 
                bank['currency'], f"{bank['balance']:,.2f}", f"{pkr:,.2f}"
            ))
        
        # Property
        for item in self.property_tree.get_children():
            self.property_tree.delete(item)
        for prop in self.data['properties']:
            zakat = prop['value'] * 0.025 if prop.get('for_trade') == 'yes' else 0
            self.property_tree.insert('', 'end', values=(
                prop['name'], prop['type'], prop['location'], 
                f"{prop['value']:,.2f}", 'Yes' if prop.get('for_trade') == 'yes' else 'No',
                f"{zakat:,.2f}"
            ))
    
    def refresh_gold(self):
        for item in self.gold_tree.get_children():
            self.gold_tree.delete(item)
        
        for gold in self.data['gold']:
            if gold['purity'] == '24':
                price = self.data['settings']['gold_price_24k']
            elif gold['purity'] == '22':
                price = self.data['settings']['gold_price_22k']
            else:
                price = self.data['settings']['gold_price_18k']
            value = gold['weight'] * price
            zakat = value * 0.025
            self.gold_tree.insert('', 'end', values=(
                gold['owner'], gold['description'], gold['weight'],
                f"{gold['purity']}K", f"{value:,.2f}", f"{zakat:,.2f}"
            ))
        
        self.gold_price_label.config(text=f"Gold Price: 24K: {self.data['settings']['gold_price_24k']:,} | 22K: {self.data['settings']['gold_price_22k']:,} | 18K: {self.data['settings']['gold_price_18k']:,} PKR/Tola")
    
    def refresh_recipients(self):
        for item in self.recipients_tree.get_children():
            self.recipients_tree.delete(item)
        for recipient in self.data['recipients']:
            total_received = sum(p['amount'] for p in self.data['payments'] if p['recipient_id'] == recipient['id'])
            self.recipients_tree.insert('', 'end', values=(
                recipient['name'], recipient['category'], recipient['nic'],
                recipient['mobile'], recipient['address'][:20] + '...' if len(recipient['address']) > 20 else recipient['address'],
                f"{total_received:,.2f}"
            ))
    
    def refresh_payments(self):
        for item in self.payments_tree.get_children():
            self.payments_tree.delete(item)
        for payment in self.data['payments']:
            recipient = next((r for r in self.data['recipients'] if r['id'] == payment['recipient_id']), None)
            self.payments_tree.insert('', 'end', values=(
                payment['date'], recipient['name'] if recipient else 'Unknown',
                f"{payment['amount']:,.2f}", payment['method'], payment['notes'][:30]
            ))
        
        available = self.calculate_total_zakat() - self.calculate_total_paid()
        self.available_funds_label.config(text=f"Available: {available:,.2f} PKR")
    
    def refresh_history(self):
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        # Scan history directory
        if os.path.exists(self.history_dir):
            for filename in os.listdir(self.history_dir):
                if filename.startswith('zakat_data_') and filename.endswith('.json'):
                    year = filename.replace('zakat_data_', '').replace('.json', '')
                    filepath = os.path.join(self.history_dir, filename)
                    try:
                        with open(filepath, 'r') as f:
                            data = json.load(f)
                            total_zakat = self.calculate_historical_zakat(data)
                            total_paid = sum(p['amount'] for p in data.get('payments', []))
                            self.history_tree.insert('', 'end', values=(
                                year, f"{total_zakat:,.2f}", f"{total_paid:,.2f}",
                                f"{total_zakat - total_paid:,.2f}", len(data.get('members', [])),
                                len(data.get('recipients', []))
                            ))
                    except:
                        pass
    
    def calculate_historical_zakat(self, data):
        """Calculate zakat for historical data"""
        total = 0
        settings = data.get('settings', {})
        rates = settings.get('currency_rates', {})
        
        for cash in data.get('cash', []):
            rate = rates.get(cash['currency'], 1)
            total += cash['amount'] * rate
        for bank in data.get('banks', []):
            rate = rates.get(bank['currency'], 1)
            total += bank['balance'] * rate
        
        zakat_rate = settings.get('zakat_rate', 2.5)
        return total * (zakat_rate / 100)
    
    # Settings and utilities
    def save_settings(self):
        try:
            self.data['settings']['zakat_rate'] = float(self.zakat_rate_entry.get())
            self.data['settings']['gold_price_24k'] = float(self.gold_24k_entry.get())
            self.data['settings']['gold_price_22k'] = float(self.gold_22k_entry.get())
            self.data['settings']['gold_price_18k'] = float(self.gold_18k_entry.get())
            
            for curr, entry in self.currency_entries.items():
                self.data['settings']['currency_rates'][curr] = float(entry.get())
            
            self.save_data()
            messagebox.showinfo("Success", "Settings saved!")
            self.refresh_all()
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers!")
    
    def change_year(self, event=None):
        new_year = int(self.year_var.get())
        if new_year != self.current_year:
            # Save current year
            self.save_data()
            # Copy to history
            hist_file = os.path.join(self.history_dir, f"zakat_data_{self.current_year}.json")
            shutil.copy(self.get_data_file(), hist_file)
            
            # Load or create new year
            self.current_year = new_year
            self.data = self.load_data()
            self.refresh_all()
    
    def create_new_year(self):
        new_year = self.current_year + 1
        if not messagebox.askyesno("Confirm", f"Create new year {new_year}?\nCurrent data will be archived."):
            return
        
        # Archive current
        hist_file = os.path.join(self.history_dir, f"zakat_data_{self.current_year}.json")
        shutil.copy(self.get_data_file(), hist_file)
        
        # Create new empty year
        self.current_year = new_year
        self.year_var.set(str(new_year))
        self.data = self.get_default_data()
        self.save_data()
        self.refresh_all()
        messagebox.showinfo("Success", f"Year {new_year} created!")
    
    def backup_data(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            initialfile=f"zakat_backup_{datetime.now().strftime('%Y%m%d')}.json"
        )
        if filename:
            with open(filename, 'w') as f:
                json.dump(self.data, f, indent=2)
            messagebox.showinfo("Success", f"Backup saved to:\n{filename}")
    
    def open_data_folder(self):
        os.system(f'open "{self.data_dir}"')
    
    def reset_all_data(self):
        if messagebox.askyesno("WARNING", "This will DELETE ALL DATA permanently!\nAre you sure?"):
            if messagebox.askyesno("FINAL WARNING", "Really sure? This cannot be undone!"):
                # Delete all data files
                for file in os.listdir(self.data_dir):
                    if file.endswith('.json'):
                        os.remove(os.path.join(self.data_dir, file))
                self.data = self.get_default_data()
                self.save_data()
                self.refresh_all()
                messagebox.showinfo("Done", "All data has been reset!")
    
    def restore_from_history(self, event):
        selected = self.history_tree.selection()
        if not selected:
            return
        year = self.history_tree.item(selected[0])['values'][0]
        if messagebox.askyesno("Confirm", f"Restore data from year {year}?\nCurrent data will be archived first."):
            # Archive current
            hist_file = os.path.join(self.history_dir, f"zakat_data_{self.current_year}.json")
            shutil.copy(self.get_data_file(), hist_file)
            
            # Restore selected year
            source_file = os.path.join(self.history_dir, f"zakat_data_{year}.json")
            shutil.copy(source_file, self.get_data_file())
            self.data = self.load_data()
            self.refresh_all()
            messagebox.showinfo("Success", f"Year {year} restored!")
    
    # Edit methods
    def edit_member(self, event):
        # Implementation for editing (similar to add dialog with pre-filled values)
        pass

if __name__ == "__main__":
    root = tk.Tk()
    app = ZakatManager(root)
    root.mainloop()

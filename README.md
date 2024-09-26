# Document Agent - Zania AI Challenge

---

**Source code**: <https://github.com/github-vikramsingh/zania-agent>

**Swagger**: <http://localhost:9002/docs#/>

**Download Embedding Model, SBERT**: <https://public.ukp.informatik.tu-darmstadt.de/reimers/sentence-transformers/v0.2/all-mpnet-base-v2.zip>

**App Demo Video** : <https://drive.google.com/file/d/1A56MEMFjbklzNK1vHCm-ImBjm-ZqLGiv/view?usp=sharing>

**Document Report** : <https://drive.google.com/file/d/1onMBslzT1n4Y7ITbMEXia8af7fbf1fNf/view?usp=drive_link>

---

The project contains all the elements to perform conversation with documents. Currently, it supports Pdf documents only.

---

## Requirements

* Python 3.10.14
* conda
* SBERT : Sentence Encoder Model

# Steps to setup/run the app on local

### Step 1: Create Virtual Environment

```console
 conda create -n agent-document python=3.10.14
```

### Step 2: Install Dependencies

```console
pip install -r requirements.txt
```

### Step 3: Run below commands on terminal to download and setup the SBERT model.

```console
export MODEL_NAME="all-mpnet-base-v2.zip"
curl -O $MODEL_NAME https://public.ukp.informatik.tu-darmstadt.de/reimers/sentence-transformers/v0.2/all-mpnet-base-v2.zip 
mkdir -p model_dir/sentence-encoder-model
unzip $MODEL_NAME -d ./model_dir/sentence-encoder-model
rm -rf $MODEL_NAME
```

**Note** : In local make sure the folder name is **sentence-encoder-model** inside model_dir folder.

### Step 4: Set OPENAI_API_KEY & SLACK_TOKEN in `agent-document.yml` file.

```consol
OPENAI_API_KEY=" ";
SLACK_TOKEN="";
```

**Note** : OPENAI_API_KEY is at 2 positions in `agent-document.yml` file.

Update the YAML file `agent-document.yml` as per requirements for local development

### Step 5: Run main.py and open swagger link

Run or Debug `src.main.py`
app_swagger : http://localhost:9002/docs#/
---

## To use Vector database in Embedded mode.

* Embedded mode is default for local development
* Create a data_weaviate/cache folder at the root level of the project.

## Sentence encoder model : SBERT

#### all-mpnet-base-v2

This is a [sentence-transformers](https://www.SBERT.net) model: It maps sentences & paragraphs to a 768 dimensional
dense vector space and can be used for tasks like clustering or semantic search.

#### Usage (Sentence-Transformers)

Using this model becomes easy when you have [sentence-transformers](https://www.SBERT.net) installed:

```
pip install -U sentence-transformers
```

### Basic API Usage

* Generate Embeddings and Answer Suer query for a pdf

### Sample API Output

```console
Question: What is vacation policy at Zania?
```

```console
[{
    "question": " What is their vacation policy?",
    "answer": "**Vacation Policy of Zania, Inc.**\n\n- **Eligibility**: \n  - All **full-time regular employees** are eligible to receive vacation time:\n    - **Immediately upon hire**\n    - **Upon completion of the introductory period**\n    - **After completing a specified number of days of employment**\n\n- **Vacation Accrual**:\n  - Vacation is calculated based on:\n    - **Your work anniversary year**\n    - **The calendar year**\n    - **The fiscal year** (specific dates to be determined by the company)\n  - **Options for Vacation Accrual**:\n    - **Option 1**: Vacation is granted in a **lump sum** based on length of service.\n    - **Option 2**: Eligible employees will **accrue vacation** at a specified rate for every period worked, up to a maximum accrual limit.\n\n- **Proration**: \n  - Vacation granted during the **first year of employment** will be **prorated** based on the hire date.\n\n- **Usage of Vacation**:\n  - Employees must request vacation from their **Manager** as far in advance as possible, but at least **a specified number of days/weeks** in advance.\n  - The company will generally grant requests for vacation, considering **business needs**.\n  - In cases where multiple employees request the same time off, **length of employment**, **seniority**, or a **collective bargaining agreement** may determine priority.\n\n- **Minimum Increments**: \n  - Vacation must be taken in increments of at least **a specified number of hours/days**.\n\n- **Leave of Absence**:\n  - The company may require employees to use any **unused vacation** during disability or family medical leave, or any other leave of absence, where permissible under local, state, and federal law.\n\n- **Encouragement to Use Vacation**: \n  - The company encourages employees to **use their vacation time**. \n\nThis policy ensures that employees have the opportunity to take time off while balancing the needs of the business.",
    "documents": [
      {
        "page_content": "hire/upon completion of your introductory period/as soon as it is received /after # days of employment]].\nYou must request vacation from your Manager as far in advance as possible, but at least [[# days/weeks]] in advance. The\nCompany will generally grant requests for vacation when possible, taking business needs into consideration. When multiple\nemployees request the same time off, their [[length of employment/seniority/collectivebargaining agreement]] may\ndetermine priority in scheduling vacation times.\nYou must take vacation in increments of at least [[# of hours/days]].\nDuring a Leave of Absence\nThe Company may require you to use any unused vacation during disability or family medical leave, or any other leave of\nabsence, where permissible under local, state, and federal law.\n[[",
        "metadata": {
          "page": 24,
          "file_path": "zania",
          "source": "download_data/handbook.pdf",
          "agent": "Document",
          "score": "0.36",
          "id": "160e129d-bcea-43aa-84b5-442dda10006f"
        }
      },
      {
        "page_content": "to use available sick leave during family and medical leave, disability leave, or other leave.\n[[Sick time accumulation will be capped at a total of [#] days per year.]]\n7.7 \nVacation\nZania, Inc. provides employees with paid vacation.\nEligibility\nAll [[fulltime regular]] employees are eligible to receive vacation time [[immediately upon hire/upon completion of the\nintroductory period/after completing # days of employment]].\nDeposits Into Your Leave Account\nVacation is calculated according to [[your work anniversary year/the calendar year/the fiscal year, which begins on [date]\nand ends on [date]]]. \n[[\nEMPLOYERS MUST CHOOSE ONE\n:]]\n[[\nOption 1\n:]]\nThe amount of vacation received each year is based on your length of service and [[is granted in a lump sum at the",
        "metadata": {
          "page": 23,
          "file_path": "zania",
          "source": "download_data/handbook.pdf",
          "agent": "Document",
          "score": "0.37",
          "id": "fa39d09f-1ffb-4ebb-bce5-1cd84cdd3374"
        }
      },
      {
        "page_content": "Vacation granted during your first year of employment will be prorated based on your hire date.\n[[\nOR\n]]\n[[\nOption 2\n:]]\nAll eligible employees will accrue [[# hours/days/weeks]] of vacation for every [[period of time]] worked, up to a maximum\naccrual of [[# hours/days/weeks]]. \nOnce you reach the maximum accrual amount, you will not accrue any additional vacation until you use some of the accrued\nbut unused vacation and the amount falls below the maximum accrual amount. You will not receive retroactive credit for any\nperiod of time in which you did not accrue vacation because you accrued the maximum amount.\nLeave Usage and Requests for Leave\nThe Company encourages you to use your vacation time. You are eligible to begin using vacation [[immediately upon",
        "metadata": {
          "page": 24,
          "file_path": "zania",
          "source": "download_data/handbook.pdf",
          "agent": "Document",
          "score": "0.37",
          "id": "8b46dade-ff2c-438d-a7fd-d7c7224eb2ce"
        }
      }
    ]
  }]
```

# **Markdown Formatted Answer from LLM**

## Question

What is vacation policy at Zania?

#### Answer

**Vacation Policy of Zania, Inc.**

- **Eligibility**:
    - All **full-time regular employees** are eligible to receive vacation time:
        - **Immediately upon hire**
        - **Upon completion of the introductory period**
        - **After completing a specified number of days of employment**
- **Vacation Accrual**:
    - Vacation is calculated based on:
        - **Your work anniversary year**
        - **The calendar year**
        - **The fiscal year** (specific dates to be determined by the company)
    - **Options for Vacation Accrual**:
        - **Option 1**:
            - Vacation is granted in a **lump sum** based on your **length of service**.
            - Vacation granted during your first year will be **prorated** based on your hire date.
        - **Option 2**:
            - Eligible employees will **accrue** a specified number of hours/days/weeks of vacation for every period
              worked.
            - There is a **maximum accrual limit**; once reached, no additional vacation will accrue until some is used.
- **Requesting Vacation**:
    - Employees must request vacation from their **Manager** as far in advance as possible, but at least **a specified
      number of days/weeks** in advance.
    - The company will generally grant requests for vacation when possible, considering **business needs**.
    - In cases where multiple employees request the same time off, **length of employment**, **seniority**, or a *
      *collective bargaining agreement** may determine priority.
- **Usage of Vacation**:
    - Employees are encouraged to use their vacation time.
    - Vacation must be taken in increments of at least **a specified number of hours/days**.
- **Leave of Absence**:
    - The company may require employees to use any **unused vacation** during disability or family medical leave, or any
      other leave of absence, where permissible under local, state, and federal law.



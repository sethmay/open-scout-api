"""Seed generator for HISTORICAL Scouts BSA rank requirement-sets (2016-2023 editions).

Scraped from the U.S. Scouting Service Project archive (usscouts.org), which mirrors the
official BSA/Scouts BSA rank requirements by effective year. One requirement-set per
distinct edition (same-year editorial corrections and org-rename-only diffs collapsed):
data/requirement-sets/<rank>-<year>.json, subject rank:<slug>, chained via `supersedes`
into the current 2024 sets (seed_rank_requirements.py).

Requirement TEXT is verbatim Scouting America copyright (includes_official_text=true +
text_rights); structure/numbering derived from the pages' <ol> markup; topical section
headers omitted. method=scraped, confidence 0.8. Source pages parsed with a stdlib
html.parser tree walk (see .workbench cache); the reviewed docs are baked below so this
generator is deterministic and reproduces the committed files byte-for-byte.
"""
from __future__ import annotations

import json
from pathlib import Path

# Newest historical edition each current 2024 set supersedes (applied by seed_rank_requirements.py).
SUPERSEDES_INTO_2024 = {
    "scout-2024": "requirement-set:scout-2023",
    "tenderfoot-2024": "requirement-set:tenderfoot-2016",
    "second-class-2024": "requirement-set:second-class-2023",
    "first-class-2024": "requirement-set:first-class-2023",
    "star-2024": "requirement-set:star-2023",
    "life-2024": "requirement-set:life-2022",
    "eagle-2024": "requirement-set:eagle-2023"
}

DOCS = json.loads(r"""
[
  {
    "id": "eagle-2016",
    "kind": "requirement-set",
    "subject": "rank:eagle",
    "effective_from": "2016-01-01",
    "effective_to": "2017-12-31",
    "supersedes": null,
    "source_document": {
      "title": "Eagle Rank Requirements (2016 Boy Scout/Scouts BSA Requirements)",
      "url": "http://usscouts.org/advance/boyscout/old/bsrank7-16.asp",
      "year": 2016
    },
    "includes_official_text": true,
    "text_rights": "Requirement text \u00a9 Scouting America, reproduced with attribution for non-commercial Scouting use; NOT licensed under this dataset's CC BY-NC-SA. See NOTICE.md.",
    "requirements": [
      {
        "number": "1",
        "text": "Be active in your troop for a period of at least six months as a Life Scout."
      },
      {
        "number": "2",
        "text": "As a Life Scout, demonstrate Scout spirit by living the Scout Oath and Scout Law. Tell how you have done your duty to God, how you have lived the Scout Oath and Scout Law in your everyday life, and how your understanding of the Scout Oath and Scout Law will guide your life in the future. List on your Eagle Scout Rank Application the names of individuals who know you personally and would be willing to provide a recommendation on your behalf, including parents/guardians, religious (if not affiliated with an organized religion, then the parent or guardian provides this reference), educational, employer (if employed), and two other references."
      },
      {
        "number": "3",
        "text": "Earn a total of 21 merit badges (10 more than required for the Life rank), including these 13 merit badges:",
        "children": [
          {
            "number": "3a",
            "text": "First Aid"
          },
          {
            "number": "3b",
            "text": "Citizenship in the Community"
          },
          {
            "number": "3c",
            "text": "Citizenship in the Nation"
          },
          {
            "number": "3d",
            "text": "Citizenship in the World"
          },
          {
            "number": "3e",
            "text": "Communication"
          },
          {
            "number": "3f",
            "text": "Cooking"
          },
          {
            "number": "3g",
            "text": "Personal Fitness"
          },
          {
            "number": "3h",
            "text": "Emergency Preparedness OR Lifesaving"
          },
          {
            "number": "3i",
            "text": "Environmental Science OR Sustainability"
          },
          {
            "number": "3j",
            "text": "Personal Management"
          },
          {
            "number": "3k",
            "text": "Swimming OR Hiking OR Cycling"
          },
          {
            "number": "3l",
            "text": "Camping , and"
          },
          {
            "number": "3m",
            "text": "Family Life"
          }
        ]
      },
      {
        "number": "4",
        "text": "While a Life Scout, serve actively in your troop for six months in one or more of the following positions of responsibility: 9 Boy Scout troop. Patrol leader, assistant senior patrol leader, senior patrol leader, troop guide, Order of the Arrow troop representative, den chief, scribe, librarian, historian, quartermaster, junior assistant Scoutmaster, chaplain aide, instructor, webmaster, or outdoor ethics guide. 9 Varsity Scout team. Captain, co-captain, program manager, squad leader, team secretary, Order of the Arrow team representative, librarian, historian quartermaster, chaplain aide, instructor, den chief. webmaster, or outdoor ethics guide. Venturing crew / Sea Scout ship. President, vice president, secretary, treasurer, quartermaster historian den chief, guide boatswain, boatswain's mate, yeoman, purser, storekeeper, or webmaster Lone Scout. Leadership responsibility in your school, religious organization, club, or elsewhere in your community."
      },
      {
        "number": "5",
        "text": "While a Life Scout, plan, develop, and give leadership to others in a service project helpful to any religious institution, any school, or your community. (The project must benefit an organization other than the Boy Scouts of America.) A project proposal must be approved by the organization benefiting from the effort, your Scoutmaster and unit committee, and the council or district before you start. You must use the Eagle Scout Service Project Workbook , BSA publication No. 512-927, in meeting this requirement. (To learn more about the Eagle Scout service project, see the Guide to Advancement , topics 9.0.2.0 through 9.0.2.15.)"
      },
      {
        "number": "6",
        "text": "While a Life Scout, participate in a Scoutmaster conference."
      }
    ],
    "provenance": {
      "sources": [
        {
          "url": "http://usscouts.org/advance/boyscout/old/bsrank7-16.asp"
        },
        {
          "citation": "U.S. Scouting Service Project archived Eagle rank requirements (2016)"
        }
      ],
      "method": "scraped",
      "verified_at": "2026-07-21",
      "confidence": 0.8,
      "notes": "Scraped from usscouts.org archived edition; verbatim requirement text \u00a9 Scouting America, structure/numbering derived; topical section headers omitted."
    },
    "notes": null
  },
  {
    "id": "eagle-2018",
    "kind": "requirement-set",
    "subject": "rank:eagle",
    "effective_from": "2018-01-01",
    "effective_to": "2022-12-31",
    "supersedes": "requirement-set:eagle-2016",
    "source_document": {
      "title": "Eagle Rank Requirements (2018 Boy Scout/Scouts BSA Requirements)",
      "url": "http://usscouts.org/advance/ScoutsBSA/old/bsrank7.asp",
      "year": 2018
    },
    "includes_official_text": true,
    "text_rights": "Requirement text \u00a9 Scouting America, reproduced with attribution for non-commercial Scouting use; NOT licensed under this dataset's CC BY-NC-SA. See NOTICE.md.",
    "requirements": [
      {
        "number": "1",
        "text": "Be active in your troop for a period of at least six months as a Life Scout."
      },
      {
        "number": "2",
        "text": "As a Life Scout, demonstrate Scout spirit by living the Scout Oath and Scout Law. Tell how you have done your duty to God, how you have lived the Scout Oath and Scout Law in your everyday life, and how your understanding of the Scout Oath and Scout Law will guide your life in the future. List on your Eagle Scout Rank Application the names of individuals who know you personally and would be willing to provide a recommendation on your behalf, including parents/guardians, religious (if not affiliated with an organized religion, then the parent or guardian provides this reference), educational, employer (if employed), and two other references."
      },
      {
        "number": "3",
        "text": "Earn a total of 21 merit badges (10 more than required for the Life rank), including these 13 merit badges:",
        "children": [
          {
            "number": "3a",
            "text": "First Aid"
          },
          {
            "number": "3b",
            "text": "Citizenship in the Community"
          },
          {
            "number": "3c",
            "text": "Citizenship in the Nation"
          },
          {
            "number": "3d",
            "text": "Citizenship in the World"
          },
          {
            "number": "3e",
            "text": "Communication"
          },
          {
            "number": "3f",
            "text": "Cooking"
          },
          {
            "number": "3g",
            "text": "Personal Fitness"
          },
          {
            "number": "3h",
            "text": "Emergency Preparedness OR Lifesaving"
          },
          {
            "number": "3i",
            "text": "Environmental Science OR Sustainability"
          },
          {
            "number": "3j",
            "text": "Personal Management"
          },
          {
            "number": "3k",
            "text": "Swimming OR Hiking OR Cycling"
          },
          {
            "number": "3l",
            "text": "Camping , and"
          },
          {
            "number": "3m",
            "text": "Family Life"
          }
        ]
      },
      {
        "number": "4",
        "text": "While a Life Scout, serve actively in your troop for six months in one or more of the following positions of responsibility: 9 Boy Scout troop. Patrol leader, assistant senior patrol leader, senior patrol leader, troop guide, Order of the Arrow troop representative, den chief, scribe, librarian, historian, quartermaster, junior assistant Scoutmaster, chaplain aide, instructor, webmaster, or outdoor ethics guide 11 Venturing crew President, vice president, secretary, treasurer, den chief, historian, guide, quartermaster, chaplain aide, or outdoor ethics guide Sea Scout ship. boatswain, boatswain's mate, purser, yeoman, storekeeper, or crew leader, media specialist, specialist, den chief, or chaplain aide. Lone Scout. Leadership responsibility in your school, religious organization, club, or elsewhere in your community."
      },
      {
        "number": "5",
        "text": "While a Life Scout, plan, develop, and give leadership to others in a service project helpful to any religious institution, any school, or your community. (The project must benefit an organization other than the Boy Scouts of America.) A project proposal must be approved by the organization benefiting from the effort, your Scoutmaster and unit committee, and the council or district before you start. You must use the Eagle Scout Service Project Workbook , BSA publication No. 512-927, in meeting this requirement. (To learn more about the Eagle Scout service project, see the Guide to Advancement , topics 9.0.2.0 through 9.0.2.15.)"
      },
      {
        "number": "6",
        "text": "While a Life Scout, participate in a Scoutmaster conference."
      }
    ],
    "provenance": {
      "sources": [
        {
          "url": "http://usscouts.org/advance/ScoutsBSA/old/bsrank7.asp"
        },
        {
          "citation": "U.S. Scouting Service Project archived Eagle rank requirements (2018)"
        }
      ],
      "method": "scraped",
      "verified_at": "2026-07-21",
      "confidence": 0.8,
      "notes": "Scraped from usscouts.org archived edition; verbatim requirement text \u00a9 Scouting America, structure/numbering derived; topical section headers omitted."
    },
    "notes": null
  },
  {
    "id": "eagle-2023",
    "kind": "requirement-set",
    "subject": "rank:eagle",
    "effective_from": "2023-01-01",
    "effective_to": "2023-12-31",
    "supersedes": "requirement-set:eagle-2018",
    "source_document": {
      "title": "Eagle Rank Requirements (2023 Boy Scout/Scouts BSA Requirements)",
      "url": "http://usscouts.org/advance/ScoutsBSA/old/rank7-23.asp",
      "year": 2023
    },
    "includes_official_text": true,
    "text_rights": "Requirement text \u00a9 Scouting America, reproduced with attribution for non-commercial Scouting use; NOT licensed under this dataset's CC BY-NC-SA. See NOTICE.md.",
    "requirements": [
      {
        "number": "1",
        "text": "Be active in your troop for a period of at least six months as a Life Scout."
      },
      {
        "number": "2",
        "text": "As a Life Scout, demonstrate Scout spirit by living the Scout Oath and Scout Law. Tell how you have done your duty to God, how you have lived the Scout Oath and Scout Law in your everyday life, and how your understanding of the Scout Oath and Scout Law will guide your life in the future. List on your Eagle Scout Rank Application the names of individuals who know you personally and would be willing to provide a recommendation on your behalf, including parents/guardians, religious (if not affiliated with an organized religion, then the parent or guardian provides this reference), educational, employer (if employed), and two other references."
      },
      {
        "number": "3",
        "text": "Earn a total of 21 merit badges (10 more than required for the Life rank), including these 14 merit badges:",
        "children": [
          {
            "number": "3a",
            "text": "First Aid"
          },
          {
            "number": "3b",
            "text": "Citizenship in the Community"
          },
          {
            "number": "3c",
            "text": "Citizenship in the Nation"
          },
          {
            "number": "3d",
            "text": "Citizenship in Society"
          },
          {
            "number": "3e",
            "text": "Citizenship in the World"
          },
          {
            "number": "3f",
            "text": "Communication"
          },
          {
            "number": "3g",
            "text": "Cooking"
          },
          {
            "number": "3h",
            "text": "Personal Fitness"
          },
          {
            "number": "3i",
            "text": "Emergency Preparedness OR Lifesaving"
          },
          {
            "number": "3j",
            "text": "Environmental Science OR Sustainability"
          },
          {
            "number": "3k",
            "text": "Personal Management"
          },
          {
            "number": "3l",
            "text": "Swimming OR Hiking OR Cycling"
          },
          {
            "number": "3m",
            "text": "Camping , and"
          },
          {
            "number": "3n",
            "text": "Family Life"
          }
        ]
      },
      {
        "number": "4",
        "text": "While a Life Scout, serve actively in your troop for six months in one or more of the following positions of responsibility: 9 Scout troop. Patrol leader, assistant senior patrol leader, senior patrol leader, troop guide, Order of the Arrow troop representative, den chief, scribe, librarian, historian, quartermaster, junior assistant Scoutmaster, chaplain aide, instructor, webmaster, or outdoor ethics guide 11 Venturing crew President, vice president, secretary, treasurer, den chief, historian, guide, quartermaster, chaplain aide, or outdoor ethics guide Sea Scout ship. boatswain, boatswain's mate, purser, yeoman, storekeeper, or crew leader, media specialist, specialist, den chief, or chaplain aide. Lone Scout. Leadership responsibility in your school, religious organization, club, or elsewhere in your community."
      },
      {
        "number": "5",
        "text": "While a Life Scout, plan, develop, and give leadership to others in a service project helpful to any religious institution, any school, or your community. (The project must benefit an organization other than the Boy Scouts of America.) A project proposal must be approved by the organization benefiting from the effort, your Scoutmaster and unit committee, and the council or district before you start. You must use the Eagle Scout Service Project Workbook , BSA publication No. 512-927, in meeting this requirement. (To learn more about the Eagle Scout service project, see the Guide to Advancement , topics 9.0.2.0 through 9.0.2.15.)"
      },
      {
        "number": "6",
        "text": "While a Life Scout, participate in a Scoutmaster conference."
      }
    ],
    "provenance": {
      "sources": [
        {
          "url": "http://usscouts.org/advance/ScoutsBSA/old/rank7-23.asp"
        },
        {
          "citation": "U.S. Scouting Service Project archived Eagle rank requirements (2023)"
        }
      ],
      "method": "scraped",
      "verified_at": "2026-07-21",
      "confidence": 0.8,
      "notes": "Scraped from usscouts.org archived edition; verbatim requirement text \u00a9 Scouting America, structure/numbering derived; topical section headers omitted."
    },
    "notes": null
  },
  {
    "id": "first-class-2016",
    "kind": "requirement-set",
    "subject": "rank:first-class",
    "effective_from": "2016-01-01",
    "effective_to": "2016-12-31",
    "supersedes": null,
    "source_document": {
      "title": "First Class Rank Requirements (2016 Boy Scout/Scouts BSA Requirements)",
      "url": "http://usscouts.org/advance/boyscout/old/bsrank4-16.asp",
      "year": 2016
    },
    "includes_official_text": true,
    "text_rights": "Requirement text \u00a9 Scouting America, reproduced with attribution for non-commercial Scouting use; NOT licensed under this dataset's CC BY-NC-SA. See NOTICE.md.",
    "requirements": [
      {
        "number": "1",
        "children": [
          {
            "number": "1a",
            "text": "Since joining, participate in 10 separate troop/patrol activities, six of which include overnight camping. These 10 activities do not include troop or patrol meetings. On at least five of the six campouts, spend the night in a tent that you pitch or other structure that you help erect. (such as a lean-to, snow cave, or tepee.)"
          },
          {
            "number": "1b",
            "text": "Explain each of the principles of Tread Lightly! and tell how you practiced them while on a campout or outing. This outing must be different from the ones used for Tenderfoot requirement 1c and Second Class requirement 1b."
          }
        ]
      },
      {
        "number": "2",
        "children": [
          {
            "number": "2a",
            "text": "Help plan a menu for one of the above campouts that includes at least one breakfast, one lunch, and one dinner and that requires cooking at least two of the meals. Tell how the menu includes the foods from MyPlate or the current USDA nutritional model and how it meets nutritional needs for the planned activity or campout."
          },
          {
            "number": "2b",
            "text": "Using the menu planned in First Class requirement 2a, make a list showing a budget and the food amounts needed to feed three or more boys. Secure the ingredients."
          },
          {
            "number": "2c",
            "text": "Show which pans, utensils, and other gear will be needed to cook and serve these meals."
          },
          {
            "number": "2d",
            "text": "Demonstrate the procedures to follow in the safe handling and storage of fresh meats, dairy products, eggs, vegetables, and other perishable food products. Show how to properly dispose of camp garbage, cans, plastic containers, and other rubbish."
          },
          {
            "number": "2e",
            "text": "On one campout, serve as cook. Supervise your assistant(s) in using a stove or building a cooking fire. Prepare the breakfast, lunch, and dinner planned in First Class requirement 2a. Supervise the cleanup."
          }
        ]
      },
      {
        "number": "3",
        "children": [
          {
            "number": "3a",
            "text": "Discuss when you should and should not use lashings."
          },
          {
            "number": "3b",
            "text": "Demonstrate tying the timber hitch and clove hitch."
          },
          {
            "number": "3c",
            "text": "Demonstrate tying the square, shear, and diagonal lashings by joining two or more poles or staves together."
          },
          {
            "number": "3d",
            "text": "Use lashings to make a useful camp gadget or structure."
          }
        ]
      },
      {
        "number": "4",
        "children": [
          {
            "number": "4a",
            "text": "Using a map and compass, complete an orienteering course that covers at least one mile and requires measuring the height and/or width of designated items (tree, tower, canyon, ditch, etc.)"
          },
          {
            "number": "4b",
            "text": "Demonstrate how to use a handheld GPS unit, GPS app on a smartphone or other electronic navigation system. Use a GPS to find your current location, a destination of your choice, and the route you will take to get there. Follow that route to arrive at your destination."
          }
        ]
      },
      {
        "number": "5",
        "children": [
          {
            "number": "5a",
            "text": "Identify or show evidence of at least 10 kinds of native plants found in your local area or campsite location. You may show evidence by identifying fallen leaves or fallen fruit that you find in the field, or as part of a collection you have made, or by photographs you have taken."
          },
          {
            "number": "5b",
            "text": "Identify two ways to obtain a weather forecast for an upcoming activity. Explain why weather forecasts are important when planning for an event."
          },
          {
            "number": "5c",
            "text": "Describe at least three natural indicators of impending hazardous weather, the potential dangerous events that might result from such weather conditions, and the appropriate actions to take."
          },
          {
            "number": "5d",
            "text": "Describe extreme weather conditions you might encounter in the outdoors in your local geographic area. Discuss how you would determine ahead of time the potential risk of these types of weather dangers, alternative planning considerations to avoid such risks, and how you would prepare for and respond to those weather conditions."
          }
        ]
      },
      {
        "number": "6",
        "children": [
          {
            "number": "6a",
            "text": "Successfully complete the BSA swimmer test. 3"
          },
          {
            "number": "6b",
            "text": "Tell what precautions must be taken for a safe trip afloat."
          },
          {
            "number": "6c",
            "text": "Identify the basic parts of a canoe, kayak, or other boat. Identify the parts of a paddle or an oar."
          },
          {
            "number": "6d",
            "text": "Describe proper body positioning in a watercraft, depending on the type and size of the vessel. Explain the importance of proper position."
          },
          {
            "number": "6e",
            "text": "With a helper and a practice victim, show a line rescue both as tender and rescuer. (The practice victim should be approximately 30 feet from shore in deep water.)"
          }
        ]
      },
      {
        "number": "7",
        "children": [
          {
            "number": "7a",
            "text": "Demonstrate bandages for a sprained ankle and for injuries on the head, the upper arm, and the collarbone."
          },
          {
            "number": "7b",
            "text": "By yourself and with a partner, show how to: Transport a person from a smoke-filled room Transport for at least 25 yards a person with a sprained ankle."
          },
          {
            "number": "7c",
            "text": "Tell the five most common signals of a heart attack. Explain the steps (procedures) in cardiopulmonary resuscitation (CPR)."
          },
          {
            "number": "7d",
            "text": "Tell what utility services exist in your home or meeting place. Describe potential hazards associated with these utilities, and tell how to respond in emergency situations."
          },
          {
            "number": "7e",
            "text": "Develop an emergency action plan for your home that includes what to do in case of fire, storm, power outage, and water outage."
          },
          {
            "number": "7f",
            "text": "Explain how to obtain potable water in an emergency."
          }
        ]
      },
      {
        "number": "8",
        "children": [
          {
            "number": "8a",
            "text": "After completing Second Class requirement 7a, be physically active at least 30 minutes every day for five days a week for four weeks. Keep track of your activities."
          },
          {
            "number": "8b",
            "text": "Share your challenges and successes in completing First Class requirement 8a. Set a goal for continuing to include physical activity as part of your daily life."
          }
        ]
      },
      {
        "number": "9",
        "children": [
          {
            "number": "9a",
            "text": "Visit and discuss with a selected individual approved by your leader (for example, an elected official, judge, attorney, civil servant, principal, or teacher) the constitutional rights and obligations of a U.S. citizen."
          },
          {
            "number": "9b",
            "text": "Investigate an environmental issue affecting your community. Share what you learned about that issue with your patrol or troop. Tell what, if anything, could be done by you or your community to address the concern."
          },
          {
            "number": "9c",
            "text": "On a Scouting or family outing, take note of the trash and garbage you produce. Before your next similar outing, decide how you can reduce, recycle, or repurpose what you take on that outing, and then put those plans into action. Compare your results."
          },
          {
            "number": "9d",
            "text": "Participate in three hours of service through one or more service projects approved by your Scoutmaster. The project(s) must not be the same service project(s) used for Tenderfoot requirement 7b and Second Class requirement 8e. Explain how your service to others relates to the Scout Law."
          }
        ]
      },
      {
        "number": "10",
        "text": "Tell someone who is eligible to join Boy Scouts, or an inactive Boy Scout, about your Scouting activities. Invite him to an outing, activity, service project or meeting. Tell him how to join, or encourage the inactive Boy Scout to become active. Share your efforts with your Scoutmaster or other adult leader."
      },
      {
        "number": "11",
        "text": "Demonstrate scout spirit by living the Scout Oath and Scout Law. Tell how you have done your duty to God and how you have lived four different points of the Scout Law (different from those points used for previous ranks) in your everyday life."
      },
      {
        "number": "12",
        "text": "While working toward the First Class rank, and after completing Second Class requirement 11, participate in a Scoutmaster conference."
      },
      {
        "number": "13",
        "text": "Successfully complete your board of review for the First Class rank."
      }
    ],
    "provenance": {
      "sources": [
        {
          "url": "http://usscouts.org/advance/boyscout/old/bsrank4-16.asp"
        },
        {
          "citation": "U.S. Scouting Service Project archived First Class rank requirements (2016)"
        }
      ],
      "method": "scraped",
      "verified_at": "2026-07-21",
      "confidence": 0.8,
      "notes": "Scraped from usscouts.org archived edition; verbatim requirement text \u00a9 Scouting America, structure/numbering derived; topical section headers omitted."
    },
    "notes": null
  },
  {
    "id": "first-class-2017",
    "kind": "requirement-set",
    "subject": "rank:first-class",
    "effective_from": "2017-01-01",
    "effective_to": "2017-12-31",
    "supersedes": "requirement-set:first-class-2016",
    "source_document": {
      "title": "First Class Rank Requirements (2017 Boy Scout/Scouts BSA Requirements)",
      "url": "http://usscouts.org/advance/boyscout/old/bsrank4-17a.asp",
      "year": 2017
    },
    "includes_official_text": true,
    "text_rights": "Requirement text \u00a9 Scouting America, reproduced with attribution for non-commercial Scouting use; NOT licensed under this dataset's CC BY-NC-SA. See NOTICE.md.",
    "requirements": [
      {
        "number": "1",
        "children": [
          {
            "number": "1a",
            "text": "Since joining Boy Scouts, participate in 10 separate troop/patrol activities, at least six of which must be held outdoors. Of the outdoor activities, at least three must include overnight camping. These activities do not include troop or patrol meetings. On campouts, spend the night in a tent that you pitch or other structure that you help erect, such as a lean-to, snow cave, or tepee."
          },
          {
            "number": "1b",
            "text": "Explain each of the principles of Tread Lightly! and tell how you practiced them while on a campout or outing. This outing must be different from the ones used for Tenderfoot requirement 1c and Second Class requirement 1b."
          }
        ]
      },
      {
        "number": "2",
        "children": [
          {
            "number": "2a",
            "text": "Help plan a menu for one of the above campouts that includes at least one breakfast, one lunch, and one dinner and that requires cooking at least two of the meals. Tell how the menu includes the foods from MyPlate or the current USDA nutritional model and how it meets nutritional needs for the planned activity or campout."
          },
          {
            "number": "2b",
            "text": "Using the menu planned in First Class requirement 2a, make a list showing a budget and the food amounts needed to feed three or more boys. Secure the ingredients."
          },
          {
            "number": "2c",
            "text": "Show which pans, utensils, and other gear will be needed to cook and serve these meals."
          },
          {
            "number": "2d",
            "text": "Demonstrate the procedures to follow in the safe handling and storage of fresh meats, dairy products, eggs, vegetables, and other perishable food products. Show how to properly dispose of camp garbage, cans, plastic containers, and other rubbish."
          },
          {
            "number": "2e",
            "text": "On one campout, serve as cook. Supervise your assistant(s) in using a stove or building a cooking fire. Prepare the breakfast, lunch, and dinner planned in First Class requirement 2a. Supervise the cleanup."
          }
        ]
      },
      {
        "number": "3",
        "children": [
          {
            "number": "3a",
            "text": "Discuss when you should and should not use lashings."
          },
          {
            "number": "3b",
            "text": "Demonstrate tying the timber hitch and clove hitch."
          },
          {
            "number": "3c",
            "text": "Demonstrate tying the square, shear, and diagonal lashings by joining two or more poles or staves together."
          },
          {
            "number": "3d",
            "text": "Use lashings to make a useful camp gadget or structure."
          }
        ]
      },
      {
        "number": "4",
        "children": [
          {
            "number": "4a",
            "text": "Using a map and compass, complete an orienteering course that covers at least one mile and requires measuring the height and/or width of designated items (tree, tower, canyon, ditch, etc.)"
          },
          {
            "number": "4b",
            "text": "Demonstrate how to use a handheld GPS unit, GPS app on a smartphone or other electronic navigation system. Use a GPS to find your current location, a destination of your choice, and the route you will take to get there. Follow that route to arrive at your destination."
          }
        ]
      },
      {
        "number": "5",
        "children": [
          {
            "number": "5a",
            "text": "Identify or show evidence of at least 10 kinds of native plants found in your local area or campsite location. You may show evidence by identifying fallen leaves or fallen fruit that you find in the field, or as part of a collection you have made, or by photographs you have taken."
          },
          {
            "number": "5b",
            "text": "Identify two ways to obtain a weather forecast for an upcoming activity. Explain why weather forecasts are important when planning for an event."
          },
          {
            "number": "5c",
            "text": "Describe at least three natural indicators of impending hazardous weather, the potential dangerous events that might result from such weather conditions, and the appropriate actions to take."
          },
          {
            "number": "5d",
            "text": "Describe extreme weather conditions you might encounter in the outdoors in your local geographic area. Discuss how you would determine ahead of time the potential risk of these types of weather dangers, alternative planning considerations to avoid such risks, and how you would prepare for and respond to those weather conditions."
          }
        ]
      },
      {
        "number": "6",
        "children": [
          {
            "number": "6a",
            "text": "Successfully complete the BSA swimmer test. 3&4"
          },
          {
            "number": "6b",
            "text": "Tell what precautions must be taken for a safe trip afloat."
          },
          {
            "number": "6c",
            "text": "Identify the basic parts of a canoe, kayak, or other boat. Identify the parts of a paddle or an oar."
          },
          {
            "number": "6d",
            "text": "Describe proper body positioning in a watercraft, depending on the type and size of the vessel. Explain the importance of proper body position in the boat."
          },
          {
            "number": "6e",
            "text": "With a helper and a practice victim, show a line rescue both as tender and rescuer. (The practice victim should be approximately 30 feet from shore in deep water.) 4"
          }
        ]
      },
      {
        "number": "7",
        "children": [
          {
            "number": "7a",
            "text": "Demonstrate bandages for a sprained ankle and for injuries on the head, the upper arm, and the collarbone."
          },
          {
            "number": "7b",
            "text": "By yourself and with a partner, show how to: Transport a person from a smoke-filled room Transport for at least 25 yards a person with a sprained ankle."
          },
          {
            "number": "7c",
            "text": "Tell the five most common signals of a heart attack. Explain the steps (procedures) in cardiopulmonary resuscitation (CPR)."
          },
          {
            "number": "7d",
            "text": "Tell what utility services exist in your home or meeting place. Describe potential hazards associated with these utilities, and tell how to respond in emergency situations."
          },
          {
            "number": "7e",
            "text": "Develop an emergency action plan for your home that includes what to do in case of fire, storm, power outage, and water outage."
          },
          {
            "number": "7f",
            "text": "Explain how to obtain potable water in an emergency."
          }
        ]
      },
      {
        "number": "8",
        "children": [
          {
            "number": "8a",
            "text": "After completing Second Class requirement 7a, be physically active at least 30 minutes every day for five days a week for four weeks. Keep track of your activities."
          },
          {
            "number": "8b",
            "text": "Share your challenges and successes in completing First Class requirement 8a. Set a goal for continuing to include physical activity as part of your daily life and develop a plan for doing so."
          }
        ]
      },
      {
        "number": "9",
        "children": [
          {
            "number": "9a",
            "text": "Visit and discuss with a selected individual approved by your leader (for example, an elected official, judge, attorney, civil servant, principal, or teacher) the constitutional rights and obligations of a U.S. citizen."
          },
          {
            "number": "9b",
            "text": "Investigate an environmental issue affecting your community. Share what you learned about that issue with your patrol or troop. Tell what, if anything, could be done by you or your community to address the concern."
          },
          {
            "number": "9c",
            "text": "On a Scouting or family outing, take note of the trash and garbage you produce. Before your next similar outing, decide how you can reduce, recycle, or repurpose what you take on that outing, and then put those plans into action. Compare your results."
          },
          {
            "number": "9d",
            "text": "Participate in three hours of service through one or more service projects approved by your Scoutmaster. The project(s) must not be the same service project(s) used for Tenderfoot requirement 7b and Second Class requirement 8e. Explain how your service to others relates to the Scout Law."
          }
        ]
      },
      {
        "number": "10",
        "text": "Tell someone who is eligible to join Boy Scouts, or an inactive Boy Scout, about your Scouting activities. Invite him to an outing, activity, service project or meeting. Tell him how to join, or encourage the inactive Boy Scout to become active. Share your efforts with your Scoutmaster or other adult leader."
      },
      {
        "number": "11",
        "text": "Demonstrate scout spirit by living the Scout Oath and Scout Law. Tell how you have done your duty to God and how you have lived four different points of the Scout Law (different from those points used for previous ranks) in your everyday life."
      },
      {
        "number": "12",
        "text": "While working toward the First Class rank, and after completing Second Class requirement 11, participate in a Scoutmaster conference."
      },
      {
        "number": "13",
        "text": "Successfully complete your board of review for the First Class rank."
      }
    ],
    "provenance": {
      "sources": [
        {
          "url": "http://usscouts.org/advance/boyscout/old/bsrank4-17a.asp"
        },
        {
          "citation": "U.S. Scouting Service Project archived First Class rank requirements (2017)"
        }
      ],
      "method": "scraped",
      "verified_at": "2026-07-21",
      "confidence": 0.8,
      "notes": "Scraped from usscouts.org archived edition; verbatim requirement text \u00a9 Scouting America, structure/numbering derived; topical section headers omitted."
    },
    "notes": null
  },
  {
    "id": "first-class-2018",
    "kind": "requirement-set",
    "subject": "rank:first-class",
    "effective_from": "2018-01-01",
    "effective_to": "2018-12-31",
    "supersedes": "requirement-set:first-class-2017",
    "source_document": {
      "title": "First Class Rank Requirements (2018 Boy Scout/Scouts BSA Requirements)",
      "url": "http://usscouts.org/advance/ScoutsBSA/old/bsrank4.asp",
      "year": 2018
    },
    "includes_official_text": true,
    "text_rights": "Requirement text \u00a9 Scouting America, reproduced with attribution for non-commercial Scouting use; NOT licensed under this dataset's CC BY-NC-SA. See NOTICE.md.",
    "requirements": [
      {
        "number": "1",
        "children": [
          {
            "number": "1a",
            "text": "Since joining Boy Scouts, participate in 10 separate troop/patrol activities, at least six of which must be held outdoors. Of the outdoor activities, at least three must include overnight camping. These activities do not include troop or patrol meetings. On campouts, spend the night in a tent that you pitch or other structure that you help erect, such as a lean-to, snow cave, or tepee."
          },
          {
            "number": "1b",
            "text": "Explain each of the principles of Tread Lightly! and tell how you practiced them on a campout or outing. This outing must be different from the ones used for Tenderfoot requirement 1c and Second Class requirement 1b."
          }
        ]
      },
      {
        "number": "2",
        "children": [
          {
            "number": "2a",
            "text": "Help plan a menu for one of the above campouts that includes at least one breakfast, one lunch, and one dinner and that requires cooking at least two of the meals. Tell how the menu includes the foods from MyPlate or the current USDA nutritional model and how it meets nutritional needs for the planned activity or campout."
          },
          {
            "number": "2b",
            "text": "Using the menu planned in First Class requirement 2a, make a list showing a budget and the food amounts needed to feed three or more boys. Secure the ingredients."
          },
          {
            "number": "2c",
            "text": "Show which pans, utensils, and other gear will be needed to cook and serve these meals."
          },
          {
            "number": "2d",
            "text": "Demonstrate the procedures to follow in the safe handling and storage of fresh meats, dairy products, eggs, vegetables, and other perishable food products. Show how to properly dispose of camp garbage, cans, plastic containers, and other rubbish."
          },
          {
            "number": "2e",
            "text": "On one campout, serve as cook. Supervise your assistant(s) in using a stove or building a cooking fire. Prepare the breakfast, lunch, and dinner planned in First Class requirement 2a. Supervise the cleanup."
          }
        ]
      },
      {
        "number": "3",
        "children": [
          {
            "number": "3a",
            "text": "Discuss when you should and should not use lashings."
          },
          {
            "number": "3b",
            "text": "Demonstrate tying the timber hitch and clove hitch."
          },
          {
            "number": "3c",
            "text": "Demonstrate tying the square, shear, and diagonal lashings by joining two or more poles or staves together."
          },
          {
            "number": "3d",
            "text": "Use lashings to make a useful camp gadget or structure."
          }
        ]
      },
      {
        "number": "4",
        "children": [
          {
            "number": "4a",
            "text": "Using a map and compass, complete an orienteering course that covers at least one mile and requires measuring the height and/or width of designated items (tree, tower, canyon, ditch, etc.)"
          },
          {
            "number": "4b",
            "text": "Demonstrate how to use a handheld GPS unit, GPS app on a smartphone or other electronic navigation system. Use a GPS to find your current location, a destination of your choice, and the route you will take to get there. Follow that route to arrive at your destination."
          }
        ]
      },
      {
        "number": "5",
        "children": [
          {
            "number": "5a",
            "text": "Identify or show evidence of at least 10 kinds of native plants found in your local area or campsite location. You may show evidence by identifying fallen leaves or fallen fruit that you find in the field, or as part of a collection you have made, or by photographs you have taken."
          },
          {
            "number": "5b",
            "text": "Identify two ways to obtain a weather forecast for an upcoming activity. Explain why weather forecasts are important when planning for an event."
          },
          {
            "number": "5c",
            "text": "Describe at least three natural indicators of impending hazardous weather, the potential dangerous events that might result from such weather conditions, and the appropriate actions to take."
          },
          {
            "number": "5d",
            "text": "Describe extreme weather conditions you might encounter in the outdoors in your local geographic area. Discuss how you would determine ahead of time the potential risk of these types of weather dangers, alternative planning considerations to avoid such risks, and how you would prepare for and respond to those weather conditions."
          }
        ]
      },
      {
        "number": "6",
        "children": [
          {
            "number": "6a",
            "text": "Successfully complete the BSA swimmer test. 4&5"
          },
          {
            "number": "6b",
            "text": "Tell what precautions must be taken for a safe trip afloat."
          },
          {
            "number": "6c",
            "text": "Identify the basic parts of a canoe, kayak, or other boat. Identify the parts of a paddle or an oar."
          },
          {
            "number": "6d",
            "text": "Describe proper body positioning in a watercraft, depending on the type and size of the vessel. Explain the importance of proper body position in the boat."
          },
          {
            "number": "6e",
            "text": "With a helper and a practice victim, show a line rescue both as tender and rescuer. (The practice victim should be approximately 30 feet from shore in deep water.) 5"
          }
        ]
      },
      {
        "number": "7",
        "children": [
          {
            "number": "7a",
            "text": "Demonstrate bandages for a sprained ankle and for injuries on the head, the upper arm, and the collarbone."
          },
          {
            "number": "7b",
            "text": "By yourself and with a partner, show how to: Transport a person from a smoke-filled room Transport for at least 25 yards a person with a sprained ankle."
          },
          {
            "number": "7c",
            "text": "Tell the five most common signals of a heart attack. Explain the steps (procedures) in cardiopulmonary resuscitation (CPR)."
          },
          {
            "number": "7d",
            "text": "Tell what utility services exist in your home or meeting place. Describe potential hazards associated with these utilities, and tell how to respond in emergency situations."
          },
          {
            "number": "7e",
            "text": "Develop an emergency action plan for your home that includes what to do in case of fire, storm, power outage, and water outage."
          },
          {
            "number": "7f",
            "text": "Explain how to obtain potable water in an emergency."
          }
        ]
      },
      {
        "number": "8",
        "children": [
          {
            "number": "8a",
            "text": "After completing Second Class requirement 7a, be physically active at least 30 minutes every day for five days a week for four weeks. Keep track of your activities."
          },
          {
            "number": "8b",
            "text": "Share your challenges and successes in completing First Class requirement 8a. Set a goal for continuing to include physical activity as part of your daily life."
          }
        ]
      },
      {
        "number": "9",
        "children": [
          {
            "number": "9a",
            "text": "Visit and discuss with a selected individual approved by your leader (for example, an elected official, judge, attorney, civil servant, principal, or teacher) the constitutional rights and obligations of a U.S. citizen."
          },
          {
            "number": "9b",
            "text": "Investigate an environmental issue affecting your community. Share what you learned about that issue with your patrol or troop. Tell what, if anything, could be done by you or your community to address the concern."
          },
          {
            "number": "9c",
            "text": "On a Scouting or family outing, take note of the trash and garbage you produce. Before your next similar outing, decide how you can reduce, recycle, or repurpose what you take on that outing, and then put those plans into action. Compare your results."
          },
          {
            "number": "9d",
            "text": "Participate in three hours of service through one or more service projects approved by your Scoutmaster. The project(s) must not be the same service project(s) used for Tenderfoot requirement 7b and Second Class requirement 8e. Explain how your service to others relates to the Scout Law."
          }
        ]
      },
      {
        "number": "10",
        "text": "Tell someone who is eligible to join Boy Scouts, or an inactive Boy Scout, about your Scouting activities. Invite him to an outing, activity, service project or meeting. Tell him how to join, or encourage the inactive Boy Scout to become active. Share your efforts with your Scoutmaster or other adult leader."
      },
      {
        "number": "11",
        "text": "Demonstrate scout spirit by living the Scout Oath and Scout Law. Tell how you have done your duty to God and how you have lived four different points of the Scout Law (different from those points used for previous ranks) in your everyday life."
      },
      {
        "number": "12",
        "text": "While working toward the First Class rank, and after completing Second Class requirement 11, participate in a Scoutmaster conference."
      },
      {
        "number": "13",
        "text": "Successfully complete your board of review for the First Class rank."
      }
    ],
    "provenance": {
      "sources": [
        {
          "url": "http://usscouts.org/advance/ScoutsBSA/old/bsrank4.asp"
        },
        {
          "citation": "U.S. Scouting Service Project archived First Class rank requirements (2018)"
        }
      ],
      "method": "scraped",
      "verified_at": "2026-07-21",
      "confidence": 0.8,
      "notes": "Scraped from usscouts.org archived edition; verbatim requirement text \u00a9 Scouting America, structure/numbering derived; topical section headers omitted."
    },
    "notes": null
  },
  {
    "id": "first-class-2019",
    "kind": "requirement-set",
    "subject": "rank:first-class",
    "effective_from": "2019-01-01",
    "effective_to": "2020-12-31",
    "supersedes": "requirement-set:first-class-2018",
    "source_document": {
      "title": "First Class Rank Requirements (2019 Boy Scout/Scouts BSA Requirements)",
      "url": "http://usscouts.org/advance/ScoutsBSA/old/rank4-19.asp",
      "year": 2019
    },
    "includes_official_text": true,
    "text_rights": "Requirement text \u00a9 Scouting America, reproduced with attribution for non-commercial Scouting use; NOT licensed under this dataset's CC BY-NC-SA. See NOTICE.md.",
    "requirements": [
      {
        "number": "1",
        "children": [
          {
            "number": "1a",
            "text": "Since joining Scouts BSA, participate in 10 separate troop/patrol activities, at least six of which must be held outdoors. Of the outdoor activities, at least three must include overnight camping. These activities do not include troop or patrol meetings. On campouts, spend the night in a tent that you pitch or other structure that you help erect, such as a lean-to, snow cave, or tepee."
          },
          {
            "number": "1b",
            "text": "Explain each of the principles of Tread Lightly! and tell how you practiced them on a campout or outing. This outing must be different from the ones used for Tenderfoot requirement 1c and Second Class requirement 1b."
          }
        ]
      },
      {
        "number": "2",
        "children": [
          {
            "number": "2a",
            "text": "Help plan a menu for one of the above campouts that includes at least one breakfast, one lunch, and one dinner and that requires cooking at least two of the meals. Tell how the menu includes the foods from MyPlate or the current USDA nutritional model and how it meets nutritional needs for the planned activity or campout."
          },
          {
            "number": "2b",
            "text": "Using the menu planned in First Class requirement 2a, make a list showing a budget and the food amounts needed to feed three or more youth. Secure the ingredients."
          },
          {
            "number": "2c",
            "text": "Show which pans, utensils, and other gear will be needed to cook and serve these meals."
          },
          {
            "number": "2d",
            "text": "Demonstrate the procedures to follow in the safe handling and storage of fresh meats, dairy products, eggs, vegetables, and other perishable food products. Show how to properly dispose of camp garbage, cans, plastic containers, and other rubbish."
          },
          {
            "number": "2e",
            "text": "On one campout, serve as cook. Supervise your assistant(s) in using a stove or building a cooking fire. Prepare the breakfast, lunch, and dinner planned in First Class requirement 2a. Supervise the cleanup."
          }
        ]
      },
      {
        "number": "3",
        "children": [
          {
            "number": "3a",
            "text": "Discuss when you should and should not use lashings."
          },
          {
            "number": "3b",
            "text": "Demonstrate tying the timber hitch and clove hitch."
          },
          {
            "number": "3c",
            "text": "Demonstrate tying the square, shear, and diagonal lashings by joining two or more poles or staves together."
          },
          {
            "number": "3d",
            "text": "Use lashings to make a useful camp gadget or structure."
          }
        ]
      },
      {
        "number": "4",
        "children": [
          {
            "number": "4a",
            "text": "Using a map and compass, complete an orienteering course that covers at least one mile and requires measuring the height and/or width of designated items (tree, tower, canyon, ditch, etc.)"
          },
          {
            "number": "4b",
            "text": "Demonstrate how to use a handheld GPS unit, GPS app on a smartphone or other electronic navigation system. Use a GPS to find your current location, a destination of your choice, and the route you will take to get there. Follow that route to arrive at your destination."
          }
        ]
      },
      {
        "number": "5",
        "children": [
          {
            "number": "5a",
            "text": "Identify or show evidence of at least 10 kinds of native plants found in your local area or campsite location. You may show evidence by identifying fallen leaves or fallen fruit that you find in the field, or as part of a collection you have made, or by photographs you have taken."
          },
          {
            "number": "5b",
            "text": "Identify two ways to obtain a weather forecast for an upcoming activity. Explain why weather forecasts are important when planning for an event."
          },
          {
            "number": "5c",
            "text": "Describe at least three natural indicators of impending hazardous weather, the potential dangerous events that might result from such weather conditions, and the appropriate actions to take."
          },
          {
            "number": "5d",
            "text": "Describe extreme weather conditions you might encounter in the outdoors in your local geographic area. Discuss how you would determine ahead of time the potential risk of these types of weather dangers, alternative planning considerations to avoid such risks, and how you would prepare for and respond to those weather conditions."
          }
        ]
      },
      {
        "number": "6",
        "children": [
          {
            "number": "6a",
            "text": "Successfully complete the BSA swimmer test. 4&5"
          },
          {
            "number": "6b",
            "text": "Tell what precautions must be taken for a safe trip afloat."
          },
          {
            "number": "6c",
            "text": "Identify the basic parts of a canoe, kayak, or other boat. Identify the parts of a paddle or an oar."
          },
          {
            "number": "6d",
            "text": "Describe proper body positioning in a watercraft, depending on the type and size of the vessel. Explain the importance of proper body position in the boat."
          },
          {
            "number": "6e",
            "text": "With a helper and a practice victim, show a line rescue both as tender and rescuer. (The practice victim should be approximately 30 feet from shore in deep water.) 5"
          }
        ]
      },
      {
        "number": "7",
        "children": [
          {
            "number": "7a",
            "text": "Demonstrate bandages for a sprained ankle and for injuries on the head, the upper arm, and the collarbone."
          },
          {
            "number": "7b",
            "text": "By yourself and with a partner, show how to: Transport a person from a smoke-filled room Transport for at least 25 yards a person with a sprained ankle."
          },
          {
            "number": "7c",
            "text": "Tell the five most common signals of a heart attack. Explain the steps (procedures) in cardiopulmonary resuscitation (CPR)."
          },
          {
            "number": "7d",
            "text": "Tell what utility services exist in your home or meeting place. Describe potential hazards associated with these utilities, and tell how to respond in emergency situations."
          },
          {
            "number": "7e",
            "text": "Develop an emergency action plan for your home that includes what to do in case of fire, storm, power outage, and water outage."
          },
          {
            "number": "7f",
            "text": "Explain how to obtain potable water in an emergency."
          }
        ]
      },
      {
        "number": "8",
        "children": [
          {
            "number": "8a",
            "text": "After completing Second Class requirement 7a, be physically active at least 30 minutes every day for five days a week for four weeks. Keep track of your activities."
          },
          {
            "number": "8b",
            "text": "Share your challenges and successes in completing First Class requirement 8a. Set a goal for continuing to include physical activity as part of your daily life."
          }
        ]
      },
      {
        "number": "9",
        "children": [
          {
            "number": "9a",
            "text": "Visit and discuss with a selected individual approved by your leader (for example, an elected official, judge, attorney, civil servant, principal, or teacher) the constitutional rights and obligations of a U.S. citizen."
          },
          {
            "number": "9b",
            "text": "Investigate an environmental issue affecting your community. Share what you learned about that issue with your patrol or troop. Tell what, if anything, could be done by you or your community to address the concern."
          },
          {
            "number": "9c",
            "text": "On a Scouting or family outing, take note of the trash and garbage you produce. Before your next similar outing, decide how you can reduce, recycle, or repurpose what you take on that outing, and then put those plans into action. Compare your results."
          },
          {
            "number": "9d",
            "text": "Participate in three hours of service through one or more service projects approved by your Scoutmaster. The project(s) must not be the same service project(s) used for Tenderfoot requirement 7b and Second Class requirement 8e. Explain how your service to others relates to the Scout Law."
          }
        ]
      },
      {
        "number": "10",
        "text": "Tell someone who is eligible to join Scouts BSA, or an inactive Scout, about your Scouting activities. Invite this person to an outing, activity, service project or meeting. Provide information on how to join, or encourage the inactive Scout to become active. Share your efforts with your Scoutmaster or other adult leader."
      },
      {
        "number": "11",
        "text": "Demonstrate scout spirit by living the Scout Oath and Scout Law. Tell how you have done your duty to God and how you have lived four different points of the Scout Law (different from those points used for previous ranks) in your everyday life."
      },
      {
        "number": "12",
        "text": "While working toward the First Class rank, and after completing Second Class requirement 11, participate in a Scoutmaster conference."
      },
      {
        "number": "13",
        "text": "Successfully complete your board of review for the First Class rank."
      }
    ],
    "provenance": {
      "sources": [
        {
          "url": "http://usscouts.org/advance/ScoutsBSA/old/rank4-19.asp"
        },
        {
          "citation": "U.S. Scouting Service Project archived First Class rank requirements (2019)"
        }
      ],
      "method": "scraped",
      "verified_at": "2026-07-21",
      "confidence": 0.8,
      "notes": "Scraped from usscouts.org archived edition; verbatim requirement text \u00a9 Scouting America, structure/numbering derived; topical section headers omitted."
    },
    "notes": null
  },
  {
    "id": "first-class-2021",
    "kind": "requirement-set",
    "subject": "rank:first-class",
    "effective_from": "2021-01-01",
    "effective_to": "2022-12-31",
    "supersedes": "requirement-set:first-class-2019",
    "source_document": {
      "title": "First Class Rank Requirements (2021 Boy Scout/Scouts BSA Requirements)",
      "url": "http://usscouts.org/advance/ScoutsBSA/old/rank4-21.asp",
      "year": 2021
    },
    "includes_official_text": true,
    "text_rights": "Requirement text \u00a9 Scouting America, reproduced with attribution for non-commercial Scouting use; NOT licensed under this dataset's CC BY-NC-SA. See NOTICE.md.",
    "requirements": [
      {
        "number": "1",
        "children": [
          {
            "number": "1a",
            "text": "Since joining Scouts BSA, participate in 10 separate troop/patrol activities, at least six of which must be held outdoors. Of the outdoor activities, at least three must include overnight camping. These activities do not include troop or patrol meetings. On campouts, spend the night in a tent that you pitch or other structure that you help erect, such as a lean-to, snow cave, or tepee."
          },
          {
            "number": "1b",
            "text": "Explain each of the principles of Tread Lightly! and tell how you practiced them on a campout or outing. This outing must be different from the ones used for Tenderfoot requirement 1c and Second Class requirement 1b."
          }
        ]
      },
      {
        "number": "2",
        "children": [
          {
            "number": "2a",
            "text": "Help plan a menu for one of the above campouts that includes at least one breakfast, one lunch, and one dinner and that requires cooking at least two of the meals. Tell how the menu includes the foods from MyPlate or the current USDA nutritional model and how it meets nutritional needs for the planned activity or campout."
          },
          {
            "number": "2b",
            "text": "Using the menu planned in First Class requirement 2a, make a list showing a budget and the food amounts needed to feed three or more youth. Secure the ingredients."
          },
          {
            "number": "2c",
            "text": "Show which pans, utensils, and other gear will be needed to cook and serve these meals."
          },
          {
            "number": "2d",
            "text": "Demonstrate the procedures to follow in the safe handling and storage of fresh meats, dairy products, eggs, vegetables, and other perishable food products. Show how to properly dispose of camp garbage, cans, plastic containers, and other rubbish."
          },
          {
            "number": "2e",
            "text": "On one campout, serve as cook. Supervise your assistant(s) in using a stove or building a cooking fire. Prepare the breakfast, lunch, and dinner planned in First Class requirement 2a. Supervise the cleanup."
          }
        ]
      },
      {
        "number": "3",
        "children": [
          {
            "number": "3a",
            "text": "Discuss when you should and should not use lashings."
          },
          {
            "number": "3b",
            "text": "Demonstrate tying the timber hitch and clove hitch."
          },
          {
            "number": "3c",
            "text": "Demonstrate tying the square, shear, and diagonal lashings by joining two or more poles or staves together."
          },
          {
            "number": "3d",
            "text": "Use lashings to make a useful camp gadget or structure."
          }
        ]
      },
      {
        "number": "4",
        "children": [
          {
            "number": "4a",
            "text": "Using a map and compass, complete an orienteering course that covers at least one mile and requires measuring the height and/or width of designated items (tree, tower, canyon, ditch, etc.)"
          },
          {
            "number": "4b",
            "text": "Demonstrate how to use a handheld GPS unit, GPS app on a smartphone or other electronic navigation system Demonstrate how to use a handheld GPS unit, GPS app on a smartphone, or other electronic navigation system while on a campout or hike. Use GPS to find your current location, a destination of your choice, and the route you will take to get there. Follow that route to arrive at your destination.. Use a GPS to find your current location, a destination of your choice, and the route you will take to get there. Follow that route to arrive at your destination."
          }
        ]
      },
      {
        "number": "5",
        "children": [
          {
            "number": "5a",
            "text": "Identify or show evidence of at least 10 kinds of native plants found in your local area or campsite location. You may show evidence by identifying fallen leaves or fallen fruit that you find in the field, or as part of a collection you have made, or by photographs you have taken."
          },
          {
            "number": "5b",
            "text": "Identify two ways to obtain a weather forecast for an upcoming activity. Explain why weather forecasts are important when planning for an event."
          },
          {
            "number": "5c",
            "text": "Describe at least three natural indicators of impending hazardous weather, the potential dangerous events that might result from such weather conditions, and the appropriate actions to take."
          },
          {
            "number": "5d",
            "text": "Describe extreme weather conditions you might encounter in the outdoors in your local geographic area. Discuss how you would determine ahead of time the potential risk of these types of weather dangers, alternative planning considerations to avoid such risks, and how you would prepare for and respond to those weather conditions."
          }
        ]
      },
      {
        "number": "6",
        "children": [
          {
            "number": "6a",
            "text": "Successfully complete the BSA swimmer test. 4&5"
          },
          {
            "number": "6b",
            "text": "Tell what precautions must be taken for a safe trip afloat."
          },
          {
            "number": "6c",
            "text": "Identify the basic parts of a canoe, kayak, or other boat. Identify the parts of a paddle or an oar."
          },
          {
            "number": "6d",
            "text": "Describe proper body positioning in a watercraft, depending on the type and size of the vessel. Explain the importance of proper body position in the boat."
          },
          {
            "number": "6e",
            "text": "With a helper and a practice victim, show a line rescue both as tender and rescuer. (The practice victim should be approximately 30 feet from shore in deep water.) 5"
          }
        ]
      },
      {
        "number": "7",
        "children": [
          {
            "number": "7a",
            "text": "Demonstrate bandages for a sprained ankle and for injuries on the head, the upper arm, and the collarbone."
          },
          {
            "number": "7b",
            "text": "By yourself and with a partner, show how to: Transport a person from a smoke-filled room Transport for at least 25 yards a person with a sprained ankle."
          },
          {
            "number": "7c",
            "text": "Tell the five most common signals of a heart attack. Explain the steps (procedures) in cardiopulmonary resuscitation (CPR)."
          },
          {
            "number": "7d",
            "text": "Tell what utility services exist in your home or meeting place. Describe potential hazards associated with these utilities, and tell how to respond in emergency situations."
          },
          {
            "number": "7e",
            "text": "Develop an emergency action plan for your home that includes what to do in case of fire, storm, power outage, and water outage."
          },
          {
            "number": "7f",
            "text": "Explain how to obtain potable water in an emergency."
          }
        ]
      },
      {
        "number": "8",
        "children": [
          {
            "number": "8a",
            "text": "After completing Second Class requirement 7a, be physically active at least 30 minutes every day for five days a week for four weeks. Keep track of your activities."
          },
          {
            "number": "8b",
            "text": "Share your challenges and successes in completing First Class requirement 8a. Set a goal for continuing to include physical activity as part of your daily life."
          }
        ]
      },
      {
        "number": "9",
        "children": [
          {
            "number": "9a",
            "text": "Visit and discuss with a selected individual approved by your leader (for example, an elected official, judge, attorney, civil servant, principal, or teacher) the constitutional rights and obligations of a U.S. citizen."
          },
          {
            "number": "9b",
            "text": "Investigate an environmental issue affecting your community. Share what you learned about that issue with your patrol or troop. Tell what, if anything, could be done by you or your community to address the concern."
          },
          {
            "number": "9c",
            "text": "On a Scouting or family outing, take note of the trash and garbage you produce. Before your next similar outing, decide how you can reduce, recycle, or repurpose what you take on that outing, and then put those plans into action. Compare your results."
          },
          {
            "number": "9d",
            "text": "Participate in three hours of service through one or more service projects approved by your Scoutmaster. The project(s) must not be the same service project(s) used for Tenderfoot requirement 7b and Second Class requirement 8e. Explain how your service to others relates to the Scout Law."
          }
        ]
      },
      {
        "number": "10",
        "text": "Tell someone who is eligible to join Scouts BSA, or an inactive Scout, about your Scouting activities. Invite this person to an outing, activity, service project or meeting. Provide information on how to join, or encourage the inactive Scout to become active. Share your efforts with your Scoutmaster or other adult leader."
      },
      {
        "number": "11",
        "text": "Demonstrate scout spirit by living the Scout Oath and Scout Law. Tell how you have done your duty to God and how you have lived four different points of the Scout Law (different from those points used for previous ranks) in your everyday life."
      },
      {
        "number": "12",
        "text": "While working toward the First Class rank, and after completing Second Class requirement 11, participate in a Scoutmaster conference."
      },
      {
        "number": "13",
        "text": "Successfully complete your board of review for the First Class rank."
      }
    ],
    "provenance": {
      "sources": [
        {
          "url": "http://usscouts.org/advance/ScoutsBSA/old/rank4-21.asp"
        },
        {
          "citation": "U.S. Scouting Service Project archived First Class rank requirements (2021)"
        }
      ],
      "method": "scraped",
      "verified_at": "2026-07-21",
      "confidence": 0.8,
      "notes": "Scraped from usscouts.org archived edition; verbatim requirement text \u00a9 Scouting America, structure/numbering derived; topical section headers omitted."
    },
    "notes": null
  },
  {
    "id": "first-class-2023",
    "kind": "requirement-set",
    "subject": "rank:first-class",
    "effective_from": "2023-01-01",
    "effective_to": "2023-12-31",
    "supersedes": "requirement-set:first-class-2021",
    "source_document": {
      "title": "First Class Rank Requirements (2023 Boy Scout/Scouts BSA Requirements)",
      "url": "http://usscouts.org/usscouts/advance/ScoutsBSA/old/rank4-23.asp",
      "year": 2023
    },
    "includes_official_text": true,
    "text_rights": "Requirement text \u00a9 Scouting America, reproduced with attribution for non-commercial Scouting use; NOT licensed under this dataset's CC BY-NC-SA. See NOTICE.md.",
    "requirements": [
      {
        "number": "1",
        "children": [
          {
            "number": "1a",
            "text": "Since joining Scouts BSA, participate in 10 separate troop/patrol activities, at least six of which must be held outdoors. Of the outdoor activities, at least three must include overnight camping. These activities do not include troop or patrol meetings. On campouts, spend the night in a tent that you pitch or other structure that you help erect, such as a lean-to, snow cave, or tepee."
          },
          {
            "number": "1b",
            "text": "Explain the potential impacts of camping, both on the environment and on other outdoor users. Explain why the Outdoor Code and Leave No Trace principles are important for protecting the outdoors."
          }
        ]
      },
      {
        "number": "2",
        "children": [
          {
            "number": "2a",
            "text": "Help plan a menu for one of the above campouts that includes at least one breakfast, one lunch, and one dinner and that requires cooking at least two of the meals. Tell how the menu includes the foods from MyPlate or the current USDA nutritional model and how it meets nutritional needs for the planned activity or campout."
          },
          {
            "number": "2b",
            "text": "Using the menu planned in First Class requirement 2a, make a list showing a budget and the food amounts needed to feed three or more youth. Secure the ingredients."
          },
          {
            "number": "2c",
            "text": "Show which pans, utensils, and other gear will be needed to cook and serve these meals."
          },
          {
            "number": "2d",
            "text": "Demonstrate the procedures to follow in the safe handling and storage of fresh meats, dairy products, eggs, vegetables, and other perishable food products. Show how to properly dispose of camp garbage, cans, plastic containers, waste water and other rubbish."
          },
          {
            "number": "2e",
            "text": "On one campout, serve as cook. Supervise your assistant(s) in using a stove or building a cooking fire. Prepare the breakfast, lunch, and dinner planned in First Class requirement 2a. Supervise the cleanup."
          }
        ]
      },
      {
        "number": "3",
        "children": [
          {
            "number": "3a",
            "text": "Discuss when you should and should not use lashings."
          },
          {
            "number": "3b",
            "text": "Demonstrate tying the timber hitch and clove hitch."
          },
          {
            "number": "3c",
            "text": "Demonstrate tying the square, shear, and diagonal lashings by joining two or more poles or staves together."
          },
          {
            "number": "3d",
            "text": "Use lashings to make a useful camp gadget or structure."
          }
        ]
      },
      {
        "number": "4",
        "children": [
          {
            "number": "4a",
            "text": "Using a map and compass, complete an orienteering course that covers at least one mile and requires measuring the height and/or width of designated items (tree, tower, canyon, ditch, etc.)"
          },
          {
            "number": "4b",
            "text": "Demonstrate how to use a handheld GPS unit, GPS app on a smartphone or other electronic navigation system Demonstrate how to use a handheld GPS unit, GPS app on a smartphone, or other electronic navigation system while on a campout or hike. Use GPS to find your current location, a destination of your choice, and the route you will take to get there. Follow that route to arrive at your destination.. Use a GPS to find your current location, a destination of your choice, and the route you will take to get there. Follow that route to arrive at your destination."
          }
        ]
      },
      {
        "number": "5",
        "children": [
          {
            "number": "5a",
            "text": "Identify or show evidence of at least 10 kinds of native plants found in your local area or campsite location. You may show evidence by identifying fallen leaves or fallen fruit that you find in the field, or as part of a collection you have made, or by photographs you have taken."
          },
          {
            "number": "5b",
            "text": "Identify two ways to obtain a weather forecast for an upcoming activity. Explain why weather forecasts are important when planning for an event."
          },
          {
            "number": "5c",
            "text": "Describe at least three natural indicators of impending hazardous weather, the potential dangerous events that might result from such weather conditions, and the appropriate actions to take."
          },
          {
            "number": "5d",
            "text": "Describe extreme weather conditions you might encounter in the outdoors in your local geographic area. Discuss how you would determine ahead of time the potential risk of these types of weather dangers, alternative planning considerations to avoid such risks, and how you would prepare for and respond to those weather conditions."
          }
        ]
      },
      {
        "number": "6",
        "children": [
          {
            "number": "6a",
            "text": "Successfully complete the BSA swimmer test. 4&5"
          },
          {
            "number": "6b",
            "text": "Tell what precautions must be taken for a safe trip afloat."
          },
          {
            "number": "6c",
            "text": "Identify the basic parts of a canoe, kayak, or other boat. Identify the parts of a paddle or an oar."
          },
          {
            "number": "6d",
            "text": "Describe proper body positioning in a watercraft, depending on the type and size of the vessel. Explain the importance of proper body position in the boat."
          },
          {
            "number": "6e",
            "text": "With a helper and a practice victim, show a line rescue both as tender and rescuer. (The practice victim should be approximately 30 feet from shore in deep water.) 5"
          }
        ]
      },
      {
        "number": "7",
        "children": [
          {
            "number": "7a",
            "text": "Demonstrate bandages for a sprained ankle and for injuries on the head, the upper arm, and the collarbone."
          },
          {
            "number": "7b",
            "text": "By yourself and with a partner, show how to: Transport a person from a smoke-filled room Transport for at least 25 yards a person with a sprained ankle."
          },
          {
            "number": "7c",
            "text": "Tell the five most common signals of a heart attack. Explain the steps (procedures) in cardiopulmonary resuscitation (CPR)."
          },
          {
            "number": "7d",
            "text": "Tell what utility services exist in your home or meeting place. Describe potential hazards associated with these utilities, and tell how to respond in emergency situations."
          },
          {
            "number": "7e",
            "text": "Develop an emergency action plan for your home that includes what to do in case of fire, storm, power outage, and water outage."
          },
          {
            "number": "7f",
            "text": "Explain how to obtain potable water in an emergency."
          }
        ]
      },
      {
        "number": "8",
        "children": [
          {
            "number": "8a",
            "text": "After completing Second Class requirement 7a, be physically active at least 30 minutes every day for five days a week for four weeks. Keep track of your activities."
          },
          {
            "number": "8b",
            "text": "Share your challenges and successes in completing First Class requirement 8a. Set a goal for continuing to include physical activity as part of your daily life."
          }
        ]
      },
      {
        "number": "9",
        "children": [
          {
            "number": "9a",
            "text": "Visit and discuss with a selected individual approved by your leader (for example, an elected official, judge, attorney, civil servant, principal, or teacher) the constitutional rights and obligations of a U.S. citizen."
          },
          {
            "number": "9b",
            "text": "Investigate an environmental issue affecting your community. Share what you learned about that issue with your patrol or troop. Tell what, if anything, could be done by you or your community to address the concern."
          },
          {
            "number": "9c",
            "text": "On a Scouting or family outing, take note of the trash and garbage you produce. Before your next similar outing, decide how you can reduce, recycle, or repurpose what you take on that outing, and then put those plans into action. Compare your results."
          },
          {
            "number": "9d",
            "text": "Participate in three hours of service through one or more service projects approved by your Scoutmaster. The project(s) must not be the same service project(s) used for Tenderfoot requirement 7b and Second Class requirement 8e. Explain how your service to others relates to the Scout Law."
          }
        ]
      },
      {
        "number": "10",
        "text": "Tell someone who is eligible to join Scouts BSA, or an inactive Scout, about your Scouting activities. Invite this person to an outing, activity, service project or meeting. Provide information on how to join, or encourage the inactive Scout to become active. Share your efforts with your Scoutmaster or other adult leader."
      },
      {
        "number": "11",
        "text": "Demonstrate scout spirit by living the Scout Oath and Scout Law. Tell how you have done your duty to God and how you have lived four different points of the Scout Law (different from those points used for previous ranks) in your everyday life."
      },
      {
        "number": "12",
        "text": "While working toward the First Class rank, and after completing Second Class requirement 11, participate in a Scoutmaster conference."
      },
      {
        "number": "13",
        "text": "Successfully complete your board of review for the First Class rank."
      }
    ],
    "provenance": {
      "sources": [
        {
          "url": "http://usscouts.org/usscouts/advance/ScoutsBSA/old/rank4-23.asp"
        },
        {
          "citation": "U.S. Scouting Service Project archived First Class rank requirements (2023)"
        }
      ],
      "method": "scraped",
      "verified_at": "2026-07-21",
      "confidence": 0.8,
      "notes": "Scraped from usscouts.org archived edition; verbatim requirement text \u00a9 Scouting America, structure/numbering derived; topical section headers omitted."
    },
    "notes": null
  },
  {
    "id": "life-2016",
    "kind": "requirement-set",
    "subject": "rank:life",
    "effective_from": "2016-01-01",
    "effective_to": "2017-12-31",
    "supersedes": null,
    "source_document": {
      "title": "Life Rank Requirements (2016 Boy Scout/Scouts BSA Requirements)",
      "url": "http://usscouts.org/advance/boyscout/old/bsrank6-16.asp",
      "year": 2016
    },
    "includes_official_text": true,
    "text_rights": "Requirement text \u00a9 Scouting America, reproduced with attribution for non-commercial Scouting use; NOT licensed under this dataset's CC BY-NC-SA. See NOTICE.md.",
    "requirements": [
      {
        "number": "1",
        "text": "Be active in your troop for at least six months as a Star Scout."
      },
      {
        "number": "2",
        "text": "As a Star Scout, demonstrate Scout spirit by living the Scout Oath and Scout Law. Tell how you have done your duty to God and how you have lived the Scout Law in your everyday life."
      },
      {
        "number": "3",
        "text": "Earn five more merit badges (so that you have 11 in all), including any three additional badges from the required list for Eagle . You may choose any of the 17 merit badges on the required list for Eagle to fulfill this requirement. See Eagle rank requirement #3 for this list. Name of Merit Badge Date Earned (Eagle required) _________________________ _________________________ (Eagle required) _________________________ _________________________ (Eagle required) _________________________ _________________________ _________________________ _________________________ _________________________ _________________________"
      },
      {
        "number": "4",
        "text": "While a Star Scout, participate in six hours of service through one or more service projects approved by your Scoutmaster. At least 3 hours of this service must be conservation related."
      },
      {
        "number": "5",
        "text": "While a Star Scout, serve actively in your troop for six months in one or more of the following positions of responsibility (or carry out a unit leader-assigned leadership project to help the troop): Boy Scout troop. Patrol leader, assistant senior patrol leader, senior patrol leader, troop guide, Order of the Arrow troop representative, den chief, scribe, librarian, historian, quartermaster, bugler, junior assistant Scoutmaster, chaplain aide, instructor, webmaster, or outdoor ethics guide 7 Varsity Scout team. Captain, co-captain, program manager, squad leader, team secretary, Order of the Arrow team representative, librarian, historian, quartermaster, chaplain aide, instructor, den chief, webmaster, or outdoor ethics guide Venturing crew / Sea Scout ship. President, vice president, secretary, treasurer, den chief, quartermaster, historian, guide, boatswain, boatswain's mate, yeoman, purser, storekeeper, or webmaster, Lone Scout. Leadership responsibility in your school, religious organization, club, or elsewhere in your community."
      },
      {
        "number": "6",
        "text": "While a Star Scout, use the Teaching EDGE method to teach another Scout (preferably younger than you) the skills from ONE of the following choices, so that he is prepared to pass those requirements to his Scoutmaster's satisfaction.",
        "children": [
          {
            "number": "6a",
            "text": "Tenderfoot - 4a and 4b (first aid)"
          },
          {
            "number": "6b",
            "text": "Second Class - 2b, 2c, and 2d (cooking/tools)"
          },
          {
            "number": "6c",
            "text": "Second Class - 3a and 3d(navigation)"
          },
          {
            "number": "6d",
            "text": "First Class - 3a, 3b, 3c, and 3d (tools)"
          },
          {
            "number": "6e",
            "text": "First Class - 4a and 4b (navigation)"
          },
          {
            "number": "6f",
            "text": "Second Class - 6a and 6b (first aid)"
          },
          {
            "number": "6g",
            "text": "First Class - 7a and 7b (first aid)"
          },
          {
            "number": "6h",
            "text": "Three requirements from one of the required Eagle merit badges, as approved by your Scoutmaster."
          }
        ]
      },
      {
        "number": "7",
        "text": "While a Star Scout, participate in a Scoutmaster conference"
      },
      {
        "number": "8",
        "text": "Successfully complete your board of review for the Life rank. 8"
      }
    ],
    "provenance": {
      "sources": [
        {
          "url": "http://usscouts.org/advance/boyscout/old/bsrank6-16.asp"
        },
        {
          "citation": "U.S. Scouting Service Project archived Life rank requirements (2016)"
        }
      ],
      "method": "scraped",
      "verified_at": "2026-07-21",
      "confidence": 0.8,
      "notes": "Scraped from usscouts.org archived edition; verbatim requirement text \u00a9 Scouting America, structure/numbering derived; topical section headers omitted."
    },
    "notes": null
  },
  {
    "id": "life-2018",
    "kind": "requirement-set",
    "subject": "rank:life",
    "effective_from": "2018-01-01",
    "effective_to": "2020-12-31",
    "supersedes": "requirement-set:life-2016",
    "source_document": {
      "title": "Life Rank Requirements (2018 Boy Scout/Scouts BSA Requirements)",
      "url": "http://usscouts.org/advance/ScoutsBSA/old/bsrank6.asp",
      "year": 2018
    },
    "includes_official_text": true,
    "text_rights": "Requirement text \u00a9 Scouting America, reproduced with attribution for non-commercial Scouting use; NOT licensed under this dataset's CC BY-NC-SA. See NOTICE.md.",
    "requirements": [
      {
        "number": "1",
        "text": "Be active in your troop for at least six months as a Star Scout."
      },
      {
        "number": "2",
        "text": "As a Star Scout, demonstrate Scout spirit by living the Scout Oath and Scout Law. Tell how you have done your duty to God and how you have lived the Scout Law in your everyday life."
      },
      {
        "number": "3",
        "text": "Earn five more merit badges (so that you have 11 in all), including any three additional badges from the required list for Eagle . You may choose any of the 17 merit badges on the required list for Eagle to fulfill this requirement. See Eagle rank requirement #3 for this list. Name of Merit Badge Date Earned (Eagle required) _________________________ _________________________ (Eagle required) _________________________ _________________________ (Eagle required) _________________________ _________________________ _________________________ _________________________ _________________________ _________________________"
      },
      {
        "number": "4",
        "text": "While a Star Scout, participate in six hours of service through one or more service projects approved by your Scoutmaster. At least 3 hours of this service must be conservation related."
      },
      {
        "number": "5",
        "text": "While a Star Scout, serve actively in your troop for six months in one or more of the following positions of responsibility (or carry out a unit leader-assigned leadership project to help the troop): Boy Scout troop. Patrol leader, assistant senior patrol leader, senior patrol leader, troop guide, Order of the Arrow troop representative, den chief, scribe, librarian, historian, quartermaster, bugler, junior assistant Scoutmaster, chaplain aide, instructor, webmaster, or outdoor ethics guide 9 Venturing crew President, vice president, secretary, treasurer, den chief, historian, guide, quartermaster, chaplain aide, or outdoor ethics guide Sea Scout ship. boatswain, boatswain's mate, purser, yeoman, storekeeper, or crew leader, media specialist, specialist, den chief, or chaplain aide. Lone Scout. Leadership responsibility in your school, religious organization, club, or elsewhere in your community."
      },
      {
        "number": "6",
        "text": "While a Star Scout, use the Teaching EDGE method to teach another Scout (preferably younger than you) the skills from ONE of the following choices, so that he is prepared to pass those requirements to his Scoutmaster's satisfaction.",
        "children": [
          {
            "number": "6a",
            "text": "Tenderfoot - 4a and 4b (first aid)"
          },
          {
            "number": "6b",
            "text": "Second Class - 2b, 2c, and 2d (cooking/camping)"
          },
          {
            "number": "6c",
            "text": "Second Class - 3a and 3d(navigation)"
          },
          {
            "number": "6d",
            "text": "First Class - 3a, 3b, 3c, and 3d (tools)"
          },
          {
            "number": "6e",
            "text": "First Class - 4a and 4b (navigation)"
          },
          {
            "number": "6f",
            "text": "Second Class - 6a and 6b (first aid)"
          },
          {
            "number": "6g",
            "text": "First Class - 7a and 7b (first aid)"
          },
          {
            "number": "6h",
            "text": "Three requirements from one of the required Eagle merit badges, as approved by your Scoutmaster."
          }
        ]
      },
      {
        "number": "7",
        "text": "While a Star Scout, participate in a Scoutmaster conference"
      },
      {
        "number": "8",
        "text": "Successfully complete your board of review for the Life rank. 10"
      }
    ],
    "provenance": {
      "sources": [
        {
          "url": "http://usscouts.org/advance/ScoutsBSA/old/bsrank6.asp"
        },
        {
          "citation": "U.S. Scouting Service Project archived Life rank requirements (2018)"
        }
      ],
      "method": "scraped",
      "verified_at": "2026-07-21",
      "confidence": 0.8,
      "notes": "Scraped from usscouts.org archived edition; verbatim requirement text \u00a9 Scouting America, structure/numbering derived; topical section headers omitted."
    },
    "notes": null
  },
  {
    "id": "life-2021",
    "kind": "requirement-set",
    "subject": "rank:life",
    "effective_from": "2021-01-01",
    "effective_to": "2021-12-31",
    "supersedes": "requirement-set:life-2018",
    "source_document": {
      "title": "Life Rank Requirements (2021 Boy Scout/Scouts BSA Requirements)",
      "url": "http://usscouts.org/advance/ScoutsBSA/old/rank6-21.asp",
      "year": 2021
    },
    "includes_official_text": true,
    "text_rights": "Requirement text \u00a9 Scouting America, reproduced with attribution for non-commercial Scouting use; NOT licensed under this dataset's CC BY-NC-SA. See NOTICE.md.",
    "requirements": [
      {
        "number": "1",
        "text": "Be active in your troop for at least six months as a Star Scout."
      },
      {
        "number": "2",
        "text": "As a Star Scout, demonstrate Scout spirit by living the Scout Oath and Scout Law. Tell how you have done your duty to God and how you have lived the Scout Law in your everyday life."
      },
      {
        "number": "3",
        "text": "Earn five more merit badges (so that you have 11 in all), including any number more from the list for Eagle so that you have a total of seven from the required list of Eagle in that total number of 11 merit badges. You may choose any of the 17 merit badges on the required list for Eagle to fulfill this requirement. See Eagle rank requirement #3 for this list."
      },
      {
        "number": "4",
        "text": "While a Star Scout, participate in six hours of service through one or more service projects approved by your Scoutmaster. At least 3 hours of this service must be conservation related."
      },
      {
        "number": "5",
        "text": "While a Star Scout, serve actively in your troop for six months in one or more of the following positions of responsibility (or carry out a unit leader-assigned leadership project to help the troop): Scout troop. Patrol leader, assistant senior patrol leader, senior patrol leader, troop guide, Order of the Arrow troop representative, den chief, scribe, librarian, historian, quartermaster, bugler, junior assistant Scoutmaster, chaplain aide, instructor, webmaster, or outdoor ethics guide 9 Venturing crew President, vice president, secretary, treasurer, den chief, historian, guide, quartermaster, chaplain aide, or outdoor ethics guide Sea Scout ship. boatswain, boatswain's mate, purser, yeoman, storekeeper, or crew leader, media specialist, specialist, den chief, or chaplain aide. Lone Scout. Leadership responsibility in your school, religious organization, club, or elsewhere in your community."
      },
      {
        "number": "6",
        "text": "While a Star Scout, use the Teaching EDGE method to teach another Scout (preferably younger than you) the skills from ONE of the following choices, so that the Scout is prepared to pass those requirements to their Scoutmaster's satisfaction.",
        "children": [
          {
            "number": "6a",
            "text": "Tenderfoot - 4a and 4b (first aid)"
          },
          {
            "number": "6b",
            "text": "Second Class - 2b, 2c, and 2d (cooking/camping)"
          },
          {
            "number": "6c",
            "text": "Second Class - 3a and 3d (navigation)"
          },
          {
            "number": "6d",
            "text": "First Class - 3a, 3b, 3c, and 3d (tools)"
          },
          {
            "number": "6e",
            "text": "First Class - 4a and 4b (navigation)"
          },
          {
            "number": "6f",
            "text": "Second Class - 6a and 6b (first aid)"
          },
          {
            "number": "6g",
            "text": "First Class - 7a and 7b (first aid)"
          },
          {
            "number": "6h",
            "text": "Three requirements from one of the required Eagle merit badges, as approved by your Scoutmaster."
          }
        ]
      },
      {
        "number": "7",
        "text": "While a Star Scout, participate in a Scoutmaster conference"
      },
      {
        "number": "8",
        "text": "Successfully complete your board of review for the Life rank. 10"
      }
    ],
    "provenance": {
      "sources": [
        {
          "url": "http://usscouts.org/advance/ScoutsBSA/old/rank6-21.asp"
        },
        {
          "citation": "U.S. Scouting Service Project archived Life rank requirements (2021)"
        }
      ],
      "method": "scraped",
      "verified_at": "2026-07-21",
      "confidence": 0.8,
      "notes": "Scraped from usscouts.org archived edition; verbatim requirement text \u00a9 Scouting America, structure/numbering derived; topical section headers omitted."
    },
    "notes": null
  },
  {
    "id": "life-2022",
    "kind": "requirement-set",
    "subject": "rank:life",
    "effective_from": "2022-01-01",
    "effective_to": "2023-12-31",
    "supersedes": "requirement-set:life-2021",
    "source_document": {
      "title": "Life Rank Requirements (2022 Boy Scout/Scouts BSA Requirements)",
      "url": "http://usscouts.org/advance/ScoutsBSA/changes/rank6-22.asp",
      "year": 2022
    },
    "includes_official_text": true,
    "text_rights": "Requirement text \u00a9 Scouting America, reproduced with attribution for non-commercial Scouting use; NOT licensed under this dataset's CC BY-NC-SA. See NOTICE.md.",
    "requirements": [
      {
        "number": "1",
        "text": "Be active in your troop for at least six months as a Star Scout."
      },
      {
        "number": "2",
        "text": "As a Star Scout, demonstrate Scout spirit by living the Scout Oath and Scout Law. Tell how you have done your duty to God and how you have lived the Scout Law in your everyday life."
      },
      {
        "number": "3",
        "text": "Earn five more merit badges (so that you have 11 in all) including any number more from the list for Eagle so that you have a total of seven from the required list of Eagle in that total number of 11 merit badges. You may choose any of the 17 merit badges on the required list for Eagle to fulfill this requirement. See Eagle rank requirement #3 for this list. Name of Merit Badge Date Earned (Eagle required) _________________________ _________________________ (Eagle required) _________________________ _________________________ (Eagle required) _________________________ _________________________ _________________________ _________________________ _________________________ _________________________"
      },
      {
        "number": "4",
        "text": "While a Star Scout, participate in six hours of service through one or more service projects approved by your Scoutmaster. At least 3 hours of this service must be conservation related."
      },
      {
        "number": "5",
        "text": "While a Star Scout, serve actively in your troop for six months in one or more of the following positions of responsibility (or carry out a unit leader-assigned leadership project to help the troop): Scout troop. Patrol leader, assistant senior patrol leader, senior patrol leader, troop guide, Order of the Arrow troop representative, den chief, scribe, librarian, historian, quartermaster, bugler, junior assistant Scoutmaster, chaplain aide, instructor, webmaster, or outdoor ethics guide 9 Venturing crew President, vice president, secretary, treasurer, den chief, historian, guide, quartermaster, chaplain aide, or outdoor ethics guide Sea Scout ship. boatswain, boatswain's mate, purser, yeoman, storekeeper, or crew leader, media specialist, specialist, den chief, or chaplain aide. Lone Scout. Leadership responsibility in your school, religious organization, club, or elsewhere in your community."
      },
      {
        "number": "6",
        "text": "While a Star Scout, use the Teaching EDGE method to teach another Scout (preferably younger than you) the skills from ONE of the following choices, so that the Scout is prepared to pass those requirements to their Scoutmaster's satisfaction.",
        "children": [
          {
            "number": "6a",
            "text": "Tenderfoot - 4a and 4b (first aid)"
          },
          {
            "number": "6b",
            "text": "Second Class - 2b, 2c, and 2d (cooking/camping)"
          },
          {
            "number": "6c",
            "text": "Second Class - 3a and 3d (navigation)"
          },
          {
            "number": "6d",
            "text": "First Class - 3a, 3b, 3c, and 3d (tools)"
          },
          {
            "number": "6e",
            "text": "First Class - 4a and 4b (navigation)"
          },
          {
            "number": "6f",
            "text": "Second Class - 6a and 6b (first aid)"
          },
          {
            "number": "6g",
            "text": "First Class - 7a and 7b (first aid)"
          },
          {
            "number": "6h",
            "text": "Three requirements from one of the required Eagle merit badges, as approved by your Scoutmaster."
          }
        ]
      },
      {
        "number": "7",
        "text": "While a Star Scout, participate in a Scoutmaster conference"
      },
      {
        "number": "8",
        "text": "Successfully complete your board of review for the Life rank. 10"
      }
    ],
    "provenance": {
      "sources": [
        {
          "url": "http://usscouts.org/advance/ScoutsBSA/changes/rank6-22.asp"
        },
        {
          "citation": "U.S. Scouting Service Project archived Life rank requirements (2022)"
        }
      ],
      "method": "scraped",
      "verified_at": "2026-07-21",
      "confidence": 0.8,
      "notes": "Scraped from usscouts.org archived edition; verbatim requirement text \u00a9 Scouting America, structure/numbering derived; topical section headers omitted."
    },
    "notes": null
  },
  {
    "id": "scout-2016",
    "kind": "requirement-set",
    "subject": "rank:scout",
    "effective_from": "2016-01-01",
    "effective_to": "2018-12-31",
    "supersedes": null,
    "source_document": {
      "title": "Scout Rank Requirements (2016 Boy Scout/Scouts BSA Requirements)",
      "url": "http://usscouts.org/advance/boyscout/old/bsrank1-16.asp",
      "year": 2016
    },
    "includes_official_text": true,
    "text_rights": "Requirement text \u00a9 Scouting America, reproduced with attribution for non-commercial Scouting use; NOT licensed under this dataset's CC BY-NC-SA. See NOTICE.md.",
    "requirements": [
      {
        "number": "1",
        "children": [
          {
            "number": "1a",
            "text": "Repeat from memory the Scout Oath, Scout Law, Scout motto, and Scout slogan. In your own words, explain their meaning."
          },
          {
            "number": "1b",
            "text": "Explain what Scout spirit is. Describe some ways you have shown Scout spirit by practicing the Scout Oath, Scout Law, Scout motto, and Scout slogan."
          },
          {
            "number": "1c",
            "text": "Demonstrate the Boy Scout sign, salute, and handshake. Explain when they should be used."
          },
          {
            "number": "1d",
            "text": "Describe the First Class Scout badge and tell what each part stands for. Explain the significance of the First Class Scout badge."
          },
          {
            "number": "1e",
            "text": "Repeat from memory the Outdoor Code. In your own words, explain what the Outdoor Code means to you."
          },
          {
            "number": "1f",
            "text": "Repeat from memory the Pledge of Allegiance. In your own words, explain its meaning."
          }
        ]
      },
      {
        "number": "2",
        "text": "After attending at least one Boy Scout troop meeting, do the following:",
        "children": [
          {
            "number": "2a",
            "text": "Describe how the Scouts in the troop provide its leadership."
          },
          {
            "number": "2b",
            "text": "Describe the four steps of Boy Scout advancement."
          },
          {
            "number": "2c",
            "text": "Describe what the Boy Scout ranks are and how they are earned."
          },
          {
            "number": "2d",
            "text": "Describe what merit badges are and how they are earned."
          }
        ]
      },
      {
        "number": "3",
        "children": [
          {
            "number": "3a",
            "text": "Explain the patrol method. Describe the types of patrols that are used in your troop."
          },
          {
            "number": "3b",
            "text": "Become familiar with your patrol name, emblem, flag, and yell. Explain how these items create patrol spirit."
          }
        ]
      },
      {
        "number": "4",
        "children": [
          {
            "number": "4a",
            "text": "Show how to tie a square knot, two half-hitches, and a taut-line hitch. Explain how each knot is used."
          },
          {
            "number": "4b",
            "text": "Show the proper care of a rope by learning how to whip and fuse the ends of different kinds of rope."
          }
        ]
      },
      {
        "number": "5",
        "text": "Demonstrate your knowledge of pocketknife safety."
      },
      {
        "number": "6",
        "text": "With your parent or guardian, complete the exercises in the pamphlet \" How to Protect Your Children from Child Abuse: A Parents Guide \" and earn the Cyber Chip Award for your grade. 1"
      },
      {
        "number": "7",
        "text": "Since joining the troop and while working on the Scout rank, participate in a Scoutmaster conference."
      }
    ],
    "provenance": {
      "sources": [
        {
          "url": "http://usscouts.org/advance/boyscout/old/bsrank1-16.asp"
        },
        {
          "citation": "U.S. Scouting Service Project archived Scout rank requirements (2016)"
        }
      ],
      "method": "scraped",
      "verified_at": "2026-07-21",
      "confidence": 0.8,
      "notes": "Scraped from usscouts.org archived edition; verbatim requirement text \u00a9 Scouting America, structure/numbering derived; topical section headers omitted."
    },
    "notes": null
  },
  {
    "id": "scout-2019",
    "kind": "requirement-set",
    "subject": "rank:scout",
    "effective_from": "2019-01-01",
    "effective_to": "2022-12-31",
    "supersedes": "requirement-set:scout-2016",
    "source_document": {
      "title": "Scout Rank Requirements (2019 Boy Scout/Scouts BSA Requirements)",
      "url": "http://usscouts.org/advance/ScoutsBSA/old/rank1-19.asp",
      "year": 2019
    },
    "includes_official_text": true,
    "text_rights": "Requirement text \u00a9 Scouting America, reproduced with attribution for non-commercial Scouting use; NOT licensed under this dataset's CC BY-NC-SA. See NOTICE.md.",
    "requirements": [
      {
        "number": "1",
        "children": [
          {
            "number": "1a",
            "text": "Repeat from memory the Scout Oath, Scout Law, Scout motto, and Scout slogan. In your own words, explain their meaning."
          },
          {
            "number": "1b",
            "text": "Explain what Scout spirit is. Describe some ways you have shown Scout spirit by practicing the Scout Oath, Scout Law, Scout motto, and Scout slogan."
          },
          {
            "number": "1c",
            "text": "Demonstrate the Scout sign, salute, and handshake. Explain when they should be used."
          },
          {
            "number": "1d",
            "text": "Describe the First Class Scout badge and tell what each part stands for. Explain the significance of the First Class Scout badge."
          },
          {
            "number": "1e",
            "text": "Repeat from memory the Outdoor Code. In your own words, explain what the Outdoor Code means to you."
          },
          {
            "number": "1f",
            "text": "Repeat from memory the Pledge of Allegiance. In your own words, explain its meaning."
          }
        ]
      },
      {
        "number": "2",
        "text": "After attending at least one Scout troop meeting, do the following:",
        "children": [
          {
            "number": "2a",
            "text": "Describe how the Scouts in the troop provide its leadership."
          },
          {
            "number": "2b",
            "text": "Describe the four steps of Scout advancement."
          },
          {
            "number": "2c",
            "text": "Describe what the Scouts BSA ranks are and how they are earned."
          },
          {
            "number": "2d",
            "text": "Describe what merit badges are and how they are earned."
          }
        ]
      },
      {
        "number": "3",
        "children": [
          {
            "number": "3a",
            "text": "Explain the patrol method. Describe the types of patrols that are used in your troop."
          },
          {
            "number": "3b",
            "text": "Become familiar with your patrol name, emblem, flag, and yell. Explain how these items create patrol spirit."
          }
        ]
      },
      {
        "number": "4",
        "children": [
          {
            "number": "4a",
            "text": "Show how to tie a square knot, two half-hitches, and a taut-line hitch. Explain how each knot is used."
          },
          {
            "number": "4b",
            "text": "Show the proper care of a rope by learning how to whip and fuse the ends of different kinds of rope."
          }
        ]
      },
      {
        "number": "5",
        "text": "Tell what you need to know about pocketknife safety."
      },
      {
        "number": "6",
        "text": "With your parent or guardian, complete the exercises in the pamphlet \" How to Protect Your Children from Child Abuse: A Parents Guide \" and earn the Cyber Chip Award for your grade. 1"
      },
      {
        "number": "7",
        "text": "Since joining the troop and while working on the Scout rank, participate in a Scoutmaster conference."
      }
    ],
    "provenance": {
      "sources": [
        {
          "url": "http://usscouts.org/advance/ScoutsBSA/old/rank1-19.asp"
        },
        {
          "citation": "U.S. Scouting Service Project archived Scout rank requirements (2019)"
        }
      ],
      "method": "scraped",
      "verified_at": "2026-07-21",
      "confidence": 0.8,
      "notes": "Scraped from usscouts.org archived edition; verbatim requirement text \u00a9 Scouting America, structure/numbering derived; topical section headers omitted."
    },
    "notes": null
  },
  {
    "id": "scout-2023",
    "kind": "requirement-set",
    "subject": "rank:scout",
    "effective_from": "2023-01-01",
    "effective_to": "2023-12-31",
    "supersedes": "requirement-set:scout-2019",
    "source_document": {
      "title": "Scout Rank Requirements (2023 Boy Scout/Scouts BSA Requirements)",
      "url": "http://usscouts.org/advance/ScoutsBSA/old/rank1-23.asp",
      "year": 2023
    },
    "includes_official_text": true,
    "text_rights": "Requirement text \u00a9 Scouting America, reproduced with attribution for non-commercial Scouting use; NOT licensed under this dataset's CC BY-NC-SA. See NOTICE.md.",
    "requirements": [
      {
        "number": "1",
        "children": [
          {
            "number": "1a",
            "text": "Repeat from memory the Scout Oath, Scout Law, Scout motto, and Scout slogan. In your own words, explain their meaning."
          },
          {
            "number": "1b",
            "text": "Explain what Scout spirit is. Describe some ways you have shown Scout spirit by practicing the Scout Oath, Scout Law, Scout motto, and Scout slogan."
          },
          {
            "number": "1c",
            "text": "Demonstrate the Scout sign, salute, and handshake. Explain when they should be used."
          },
          {
            "number": "1d",
            "text": "Describe the First Class Scout badge and tell what each part stands for. Explain the significance of the First Class Scout badge."
          },
          {
            "number": "1e",
            "text": "Repeat from memory the Outdoor Code. List the seven principles of Leave No Trace. Explain the difference between the two."
          },
          {
            "number": "1f",
            "text": "Repeat from memory the Pledge of Allegiance. In your own words, explain its meaning."
          }
        ]
      },
      {
        "number": "2",
        "text": "After attending at least one Scout troop meeting, do the following:",
        "children": [
          {
            "number": "2a",
            "text": "Describe how the Scouts in the troop provide its leadership."
          },
          {
            "number": "2b",
            "text": "Describe the four steps of Scout advancement."
          },
          {
            "number": "2c",
            "text": "Describe what the Scouts BSA ranks are and how they are earned."
          },
          {
            "number": "2d",
            "text": "Describe what merit badges are and how they are earned."
          }
        ]
      },
      {
        "number": "3",
        "children": [
          {
            "number": "3a",
            "text": "Explain the patrol method. Describe the types of patrols that are used in your troop."
          },
          {
            "number": "3b",
            "text": "Become familiar with your patrol name, emblem, flag, and yell. Explain how these items create patrol spirit."
          }
        ]
      },
      {
        "number": "4",
        "children": [
          {
            "number": "4a",
            "text": "Show how to tie a square knot, two half-hitches, and a taut-line hitch. Explain how each knot is used."
          },
          {
            "number": "4b",
            "text": "Show the proper care of a rope by learning how to whip and fuse the ends of different kinds of rope."
          }
        ]
      },
      {
        "number": "5",
        "text": "Tell what you need to know about pocketknife safety and responsibly."
      },
      {
        "number": "6",
        "text": "With your parent or guardian, complete the exercises in the pamphlet \" How to Protect Your Children from Child Abuse: A Parents Guide \" and earn the Cyber Chip Award for your grade or view the Personal Safety Awareness videos ( with your parent or Guardian's permission). 1"
      },
      {
        "number": "7",
        "text": "Since joining the troop and while working on the Scout rank, participate in a Scoutmaster conference."
      }
    ],
    "provenance": {
      "sources": [
        {
          "url": "http://usscouts.org/advance/ScoutsBSA/old/rank1-23.asp"
        },
        {
          "citation": "U.S. Scouting Service Project archived Scout rank requirements (2023)"
        }
      ],
      "method": "scraped",
      "verified_at": "2026-07-21",
      "confidence": 0.8,
      "notes": "Scraped from usscouts.org archived edition; verbatim requirement text \u00a9 Scouting America, structure/numbering derived; topical section headers omitted."
    },
    "notes": null
  },
  {
    "id": "second-class-2016",
    "kind": "requirement-set",
    "subject": "rank:second-class",
    "effective_from": "2016-01-01",
    "effective_to": "2016-12-31",
    "supersedes": null,
    "source_document": {
      "title": "Second Class Rank Requirements (2016 Boy Scout/Scouts BSA Requirements)",
      "url": "http://usscouts.org/advance/boyscout/old/bsrank3-16.asp",
      "year": 2016
    },
    "includes_official_text": true,
    "text_rights": "Requirement text \u00a9 Scouting America, reproduced with attribution for non-commercial Scouting use; NOT licensed under this dataset's CC BY-NC-SA. See NOTICE.md.",
    "requirements": [
      {
        "number": "1",
        "children": [
          {
            "number": "1a",
            "text": "Since joining, participate in five separate troop/patrol activities, three of which include overnight camping. These five activities do not include troop or patrol meetings. On at least two of the three campouts, spend the night in a tent that you pitch or other structure that you help erect (such as a lean-to, snow cave, or tepee.)"
          },
          {
            "number": "1b",
            "text": "Explain the principles of Leave No Trace, and tell how you practiced them while on a campout or outing. This outing must be different from the one used for Tenderfoot requirement 1c."
          },
          {
            "number": "1c",
            "text": "On one of these campouts, select a location for your patrol site and recommend it to your patrol leader, senior patrol leader, or troop guide. Explain what factors you should consider when choosing a patrol site and where to pitch a tent."
          }
        ]
      },
      {
        "number": "2",
        "children": [
          {
            "number": "2a",
            "text": "Explain when it is appropriate to use a fire for cooking or other purposes and when it would not be appropriate to do so."
          },
          {
            "number": "2b",
            "text": "Use the tools listed in Tenderfoot requirement 3d to prepare tinder, kindling, and fuel wood for a cooking fire."
          },
          {
            "number": "2c",
            "text": "At an approved outdoor location and time, use the tinder, kindling, and fuel wood from Second Class requirement 2b to demonstrate how to build a fire. Unless prohibited by local fire restrictions, light the fire. After allowing the flames to burn safely for at least two minutes, safely extinguish the flames with minimal impact to the fire site."
          },
          {
            "number": "2d",
            "text": "Explain when it is appropriate to use a lightweight stove and when it is appropriate to use a propane stove. Set up a lightweight stove or propane stove. Light the stove, unless prohibited by local fire restrictions. Describe the safety procedures for using these types of stoves."
          },
          {
            "number": "2e",
            "text": "On one campout, plan and cook one hot breakfast or lunch, selecting foods from MyPlate or the current USDA nutrition model. Explain the importance of good nutrition. Demonstrate how to transport, store, and prepare the foods you selected."
          },
          {
            "number": "2f",
            "text": "Demonstrate how to tie the sheet bend knot. Describe a situation in which you would use this knot."
          },
          {
            "number": "2g",
            "text": "Demonstrate how to tie the bowline knot. Describe a situation in which you would use this knot."
          }
        ]
      },
      {
        "number": "3",
        "children": [
          {
            "number": "3a",
            "text": "Demonstrate how a compass works and how to orient a map. Use a map to point out and tell the meaning of five map symbols."
          },
          {
            "number": "3b",
            "text": "Using a compass and a map together, take a five-mile hike (or 10 miles by bike) approved by your adult leader and your parent or guardian. 2"
          },
          {
            "number": "3c",
            "text": "Describe some hazards or injuries that you might encounter on your hike and what you can do to help prevent them. 2"
          },
          {
            "number": "3d",
            "text": "Demonstrate how to find directions during the day and at night without using a compass or an electronic device."
          }
        ]
      },
      {
        "number": "4",
        "text": "Identify or show evidence of at least ten kinds of wild animals (such as birds, mammals, reptiles, fish, mollusks) found in your local area or camping location. You may show evidence by tracks, signs, or photographs you have taken."
      },
      {
        "number": "5",
        "children": [
          {
            "number": "5a",
            "text": "Tell what precautions must be taken for a safe swim."
          },
          {
            "number": "5b",
            "text": "Demonstrate your ability to pass the BSA beginner test. Jump feetfirst into water over your head in depth, level off and swim 25 feet on the surface, stop, turn sharply, resume swimming, then return to your starting place."
          },
          {
            "number": "5c",
            "text": "Demonstrate water rescue methods by reaching with your arm or leg, by reaching with a suitable object, and by throwing lines and objects."
          },
          {
            "number": "5d",
            "text": "Explain why swimming rescues should not be attempted when a reaching or throwing rescue is possible. Explain why and how a rescue swimmer should avoid contact with the victim."
          }
        ]
      },
      {
        "number": "6",
        "children": [
          {
            "number": "6a",
            "text": "Demonstrate first aid for the following: Object in the eye Bite of a warm blooded animal Puncture wounds from a splinter, nail, and fishhook Serious burns (partial thickness, or second degree) Heat exhaustion Shock Heatstroke, dehydration, hypothermia, and hyperventilation"
          },
          {
            "number": "6b",
            "text": "Show what to do for \"hurry\" cases of stopped breathing, stroke, severe bleeding, and ingested poisoning."
          },
          {
            "number": "6c",
            "text": "Tell what you can do while on a campout or hike to prevent or reduce the occurrence of the injuries listed in Second Class requirements 6a and 6b."
          },
          {
            "number": "6d",
            "text": "Explain what to do in case of accidents that require emergency response in the home and the backcountry. Explain what constitutes an emergency and what information you will need to provide to a responder."
          },
          {
            "number": "6e",
            "text": "Tell how you should respond if you come upon the scene of a vehicular accident."
          }
        ]
      },
      {
        "number": "7",
        "children": [
          {
            "number": "7a",
            "text": "After competing Tenderfoot requirement 6c, be physically active at least 30 minutes a day for five days a week for four weeks. Keep track of your activities."
          },
          {
            "number": "7b",
            "text": "Share your challenges and successes in completing Second Class requirement 7a. Set a goal for continuing to include physical activity as part of your daily life and develop a plan for doing so."
          },
          {
            "number": "7c",
            "text": "Participate in a school, community, or troop program on the dangers of using drugs, alcohol, and tobacco, and other practices that could be harmful to your health. Discuss your participation in the program with your family, and explain the dangers of substance addictions. Report to your Scoutmaster or other adult leader in your troop about which parts of the Scout Oath and Law relate to what you learned."
          }
        ]
      },
      {
        "number": "8",
        "children": [
          {
            "number": "8a",
            "text": "Participate in a flag ceremony for your school, religious institution, chartered organization, community, or Scouting activity."
          },
          {
            "number": "8b",
            "text": "Explain what respect is due the flag of the United States."
          },
          {
            "number": "8c",
            "text": "With your parents or guardian, decide on an amount of money that you would like to earn, based on the cost of a specific item you would like to purchase. Develop a written plan to earn the amount agreed upon and follow that plan; it is acceptable to make changes to your plan along the way. Discuss any changes made to your original plan and whether you met your goal."
          },
          {
            "number": "8d",
            "text": "At a minimum of three locations, compare the cost of the item for which you are saving to determine the best place to purchase it. After completing Second Class requirement 8c, decide if you will use the amount that you earned as originally intended, save all or part of it, or use it for another purpose."
          },
          {
            "number": "8e",
            "text": "Participate in two hours of service through one or more service projects approved by your Scoutmaster. Tell how your service to others relates to the Scout Oath."
          }
        ]
      },
      {
        "number": "9",
        "children": [
          {
            "number": "9a",
            "text": "Explain the three R's of personal safety and protection."
          },
          {
            "number": "9b",
            "text": "Describe bullying; tell what the appropriate response is to someone who is bullying you or another person."
          }
        ]
      },
      {
        "number": "10",
        "text": "Demonstrate scout spirit by living the Scout Oath and Scout Law. Tell how you have done your duty to God and how you have lived four different points of the Scout Law (not to include those used for Tenderfoot requirement 9) in your everyday life."
      },
      {
        "number": "11",
        "text": "While working toward the Second Class rank, and after completing Tenderfoot requirement 10, participate in a Scoutmaster conference."
      },
      {
        "number": "12",
        "text": "Successfully complete your board of review for the Second Class rank."
      }
    ],
    "provenance": {
      "sources": [
        {
          "url": "http://usscouts.org/advance/boyscout/old/bsrank3-16.asp"
        },
        {
          "citation": "U.S. Scouting Service Project archived Second Class rank requirements (2016)"
        }
      ],
      "method": "scraped",
      "verified_at": "2026-07-21",
      "confidence": 0.8,
      "notes": "Scraped from usscouts.org archived edition; verbatim requirement text \u00a9 Scouting America, structure/numbering derived; topical section headers omitted."
    },
    "notes": null
  },
  {
    "id": "second-class-2017",
    "kind": "requirement-set",
    "subject": "rank:second-class",
    "effective_from": "2017-01-01",
    "effective_to": "2017-12-31",
    "supersedes": "requirement-set:second-class-2016",
    "source_document": {
      "title": "Second Class Rank Requirements (2017 Boy Scout/Scouts BSA Requirements)",
      "url": "http://usscouts.org/advance/boyscout/old/bsrank3-17a.asp",
      "year": 2017
    },
    "includes_official_text": true,
    "text_rights": "Requirement text \u00a9 Scouting America, reproduced with attribution for non-commercial Scouting use; NOT licensed under this dataset's CC BY-NC-SA. See NOTICE.md.",
    "requirements": [
      {
        "number": "1",
        "children": [
          {
            "number": "1a",
            "text": "Since joining Boy Scouts, participate in five separate troop/patrol activities, at least three of which must be held outdoors. Of the outdoor activities, at least two must include overnight camping. These activities do not include troop or patrol meetings. On campouts, spend the night in a tent that you pitch or other structure that you help erect, such as a lean-to, snow cave, or tepee."
          },
          {
            "number": "1b",
            "text": "Explain the principles of Leave No Trace, and tell how you practiced them while on a campout or outing. This outing must be different from the one used for Tenderfoot requirement 1c."
          },
          {
            "number": "1c",
            "text": "On one of these campouts, select a location for your patrol site and recommend it to your patrol leader, senior patrol leader, or troop guide. Explain what factors you should consider when choosing a patrol site and where to pitch a tent."
          }
        ]
      },
      {
        "number": "2",
        "children": [
          {
            "number": "2a",
            "text": "Explain when it is appropriate to use a fire for cooking or other purposes and when it would not be appropriate to do so."
          },
          {
            "number": "2b",
            "text": "Use the tools listed in Tenderfoot requirement 3d to prepare tinder, kindling, and fuel wood for a cooking fire."
          },
          {
            "number": "2c",
            "text": "At an approved outdoor location and time, use the tinder, kindling, and fuel wood from Second Class requirement 2b to demonstrate how to build a fire. Unless prohibited by local fire restrictions, light the fire. After allowing the flames to burn safely for at least two minutes, safely extinguish the flames with minimal impact to the fire site."
          },
          {
            "number": "2d",
            "text": "Explain when it is appropriate to use a lightweight stove and when it is appropriate to use a propane stove. Set up a lightweight stove or propane stove. Unless prohibited by local fire restrictions, light the stove. Describe the safety procedures for using these types of stoves."
          },
          {
            "number": "2e",
            "text": "On one campout, plan and cook one hot breakfast or lunch, selecting foods from MyPlate or the current USDA nutritional model. Explain the importance of good nutrition. Demonstrate how to transport, store, and prepare the foods you selected."
          },
          {
            "number": "2f",
            "text": "Demonstrate how to tie the sheet bend knot. Describe a situation in which you would use this knot."
          },
          {
            "number": "2g",
            "text": "Demonstrate how to tie the bowline knot. Describe a situation in which you would use this knot."
          }
        ]
      },
      {
        "number": "3",
        "children": [
          {
            "number": "3a",
            "text": "Demonstrate how a compass works and how to orient a map. Use a map to point out and tell the meaning of five map symbols."
          },
          {
            "number": "3b",
            "text": "Using a compass and a map together, take a five-mile hike (or 10 miles by bike) approved by your adult leader and your parent or guardian. 2"
          },
          {
            "number": "3c",
            "text": "Describe some hazards or injuries that you might encounter on your hike and what you can do to help prevent them. 2"
          },
          {
            "number": "3d",
            "text": "Demonstrate how to find directions during the day and at night without using a compass or an electronic device."
          }
        ]
      },
      {
        "number": "4",
        "text": "Identify or show evidence of at least ten kinds of wild animals (such as birds, mammals, reptiles, fish, mollusks) found in your local area or camping location. You may show evidence by tracks, signs, or photographs you have taken."
      },
      {
        "number": "5",
        "children": [
          {
            "number": "5a",
            "text": "Tell what precautions must be taken for a safe swim."
          },
          {
            "number": "5b",
            "text": "Demonstrate your ability to pass the BSA beginner test. Jump feetfirst into water over your head in depth, level off and swim 25 feet on the surface, stop, turn sharply, resume swimming, then return to your starting place. 3"
          },
          {
            "number": "5c",
            "text": "Demonstrate water rescue methods by reaching with your arm or leg, by reaching with a suitable object, and by throwing lines and objects. 3"
          },
          {
            "number": "5d",
            "text": "Explain why swimming rescues should not be attempted when a reaching or throwing rescue is possible. Explain why and how a rescue swimmer should avoid contact with the victim."
          }
        ]
      },
      {
        "number": "6",
        "children": [
          {
            "number": "6a",
            "text": "Demonstrate first aid for the following: Object in the eye Bite of a warm blooded animal Puncture wounds from a splinter, nail, and fishhook Serious burns (partial thickness, or second degree) Heat exhaustion Shock Heatstroke, dehydration, hypothermia, and hyperventilation"
          },
          {
            "number": "6b",
            "text": "Show what to do for \"hurry\" cases of stopped breathing, stroke, severe bleeding, and ingested poisoning."
          },
          {
            "number": "6c",
            "text": "Tell what you can do while on a campout or hike to prevent or reduce the occurrence of the injuries listed in Second Class requirements 6a and 6b."
          },
          {
            "number": "6d",
            "text": "Explain what to do in case of accidents that require emergency response in the home and the backcountry. Explain what constitutes an emergency and what information you will need to provide to a responder."
          },
          {
            "number": "6e",
            "text": "Tell how you should respond if you come upon the scene of a vehicular accident."
          }
        ]
      },
      {
        "number": "7",
        "children": [
          {
            "number": "7a",
            "text": "After completing Tenderfoot requirement 6c, be physically active at least 30 minutes a day for five days a week for four weeks. Keep track of your activities."
          },
          {
            "number": "7b",
            "text": "Share your challenges and successes in completing Second Class requirement 7a. Set a goal for continuing to include physical activity as part of your daily life and develop a plan for doing so."
          },
          {
            "number": "7c",
            "text": "Participate in a school, community, or troop program on the dangers of using drugs, alcohol, and tobacco, and other practices that could be harmful to your health. Discuss your participation in the program with your family, and explain the dangers of substance addictions. Report to your Scoutmaster or other adult leader in your troop about which parts of the Scout Oath and Law relate to what you learned."
          }
        ]
      },
      {
        "number": "8",
        "children": [
          {
            "number": "8a",
            "text": "Participate in a flag ceremony for your school, religious institution, chartered organization, community, or Scouting activity."
          },
          {
            "number": "8b",
            "text": "Explain what respect is due the flag of the United States."
          },
          {
            "number": "8c",
            "text": "With your parents or guardian, decide on an amount of money that you would like to earn, based on the cost of a specific item you would like to purchase. Develop a written plan to earn the amount agreed upon and follow that plan; it is acceptable to make changes to your plan along the way. Discuss any changes made to your original plan and whether you met your goal."
          },
          {
            "number": "8d",
            "text": "At a minimum of three locations, compare the cost of the item for which you are saving to determine the best place to purchase it. After completing Second Class requirement 8c, decide if you will use the amount that you earned as originally intended, save all or part of it, or use it for another purpose."
          },
          {
            "number": "8e",
            "text": "Participate in two hours of service through one or more service projects approved by your Scoutmaster. Explain how your service to others relates to the Scout Oath."
          }
        ]
      },
      {
        "number": "9",
        "children": [
          {
            "number": "9a",
            "text": "Explain the three R's of personal safety and protection."
          },
          {
            "number": "9b",
            "text": "Describe bullying; tell what the appropriate response is to someone who is bullying you or another person."
          }
        ]
      },
      {
        "number": "10",
        "text": "Demonstrate scout spirit by living the Scout Oath and Scout Law. Tell how you have done your duty to God and how you have lived four different points of the Scout Law (not to include those used for Tenderfoot requirement 9) in your everyday life."
      },
      {
        "number": "11",
        "text": "While working toward the Second Class rank, and after completing Tenderfoot requirement 10, participate in a Scoutmaster conference."
      },
      {
        "number": "12",
        "text": "Successfully complete your board of review for the Second Class rank."
      }
    ],
    "provenance": {
      "sources": [
        {
          "url": "http://usscouts.org/advance/boyscout/old/bsrank3-17a.asp"
        },
        {
          "citation": "U.S. Scouting Service Project archived Second Class rank requirements (2017)"
        }
      ],
      "method": "scraped",
      "verified_at": "2026-07-21",
      "confidence": 0.8,
      "notes": "Scraped from usscouts.org archived edition; verbatim requirement text \u00a9 Scouting America, structure/numbering derived; topical section headers omitted."
    },
    "notes": null
  },
  {
    "id": "second-class-2018",
    "kind": "requirement-set",
    "subject": "rank:second-class",
    "effective_from": "2018-01-01",
    "effective_to": "2018-12-31",
    "supersedes": "requirement-set:second-class-2017",
    "source_document": {
      "title": "Second Class Rank Requirements (2018 Boy Scout/Scouts BSA Requirements)",
      "url": "http://usscouts.org/advance/ScoutsBSA/old/bsrank3.asp",
      "year": 2018
    },
    "includes_official_text": true,
    "text_rights": "Requirement text \u00a9 Scouting America, reproduced with attribution for non-commercial Scouting use; NOT licensed under this dataset's CC BY-NC-SA. See NOTICE.md.",
    "requirements": [
      {
        "number": "1",
        "children": [
          {
            "number": "1a",
            "text": "Since joining Boy Scouts, participate in five separate troop/patrol activities, at least three of which must be held outdoors. Of the outdoor activities, at least two must include overnight camping. These activities do not include troop or patrol meetings. On campouts, spend the night in a tent that you pitch or other structure that you help erect, such as a lean-to, snow cave, or tepee."
          },
          {
            "number": "1b",
            "text": "Explain the principles of Leave No Trace, and tell how you practiced them on a campout or outing. This outing must be different from the one used for Tenderfoot requirement 1c."
          },
          {
            "number": "1c",
            "text": "On one of these campouts, select a location for your patrol site and recommend it to your patrol leader, senior patrol leader, or troop guide. Explain what factors you should consider when choosing a patrol site and where to pitch a tent."
          }
        ]
      },
      {
        "number": "2",
        "children": [
          {
            "number": "2a",
            "text": "Explain when it is appropriate to use a fire for cooking or other purposes and when it would not be appropriate to do so."
          },
          {
            "number": "2b",
            "text": "Use the tools listed in Tenderfoot requirement 3d to prepare tinder, kindling, and fuel wood for a cooking fire."
          },
          {
            "number": "2c",
            "text": "At an approved outdoor location and time, use the tinder, kindling, and fuel wood from Second Class requirement 2b to demonstrate how to build a fire. Unless prohibited by local fire restrictions, light the fire. After allowing the flames to burn safely for at least two minutes, safely extinguish the flames with minimal impact to the fire site."
          },
          {
            "number": "2d",
            "text": "Explain when it is appropriate to use a lightweight stove and when it is appropriate to use a propane stove. Set up a lightweight stove or propane stove. Unless prohibited by local fire restrictions, light the stove. Describe the safety procedures for using these types of stoves."
          },
          {
            "number": "2e",
            "text": "On one campout, plan and cook one hot breakfast or lunch, selecting foods from MyPlate or the current USDA nutritional model. Explain the importance of good nutrition. Demonstrate how to transport, store, and prepare the foods you selected."
          },
          {
            "number": "2f",
            "text": "Demonstrate tying the sheet bend knot. Describe a situation in which you would use this knot."
          },
          {
            "number": "2g",
            "text": "Demonstrate tying the bowline knot. Describe a situation in which you would use this knot."
          }
        ]
      },
      {
        "number": "3",
        "children": [
          {
            "number": "3a",
            "text": "Demonstrate how a compass works and how to orient a map. Use a map to point out and tell the meaning of five map symbols."
          },
          {
            "number": "3b",
            "text": "Using a compass and map together, take a five-mile hike (or 10 miles by bike) approved by your adult leader and your parent or guardian. 2"
          },
          {
            "number": "3c",
            "text": "Describe some hazards or injuries that you might encounter on your hike and what you can do to help prevent them. 2"
          },
          {
            "number": "3d",
            "text": "Demonstrate how to find directions during the day and at night without using a compass or an electronic device."
          }
        ]
      },
      {
        "number": "4",
        "text": "Identify or show evidence of at least ten kinds of wild animals (such as birds, mammals, reptiles, fish, mollusks) found in your local area or camping location. You may show evidence by tracks, signs, or photographs you have taken."
      },
      {
        "number": "5",
        "children": [
          {
            "number": "5a",
            "text": "Tell what precautions must be taken for a safe swim."
          },
          {
            "number": "5b",
            "text": "Demonstrate your ability to pass the BSA beginner test. Jump feetfirst into water over your head in depth, level off and swim 25 feet on the surface, stop, turn sharply, resume swimming, then return to your starting place. 3"
          },
          {
            "number": "5c",
            "text": "Demonstrate water rescue methods by reaching with your arm or leg, by reaching with a suitable object, and by throwing lines and objects. 3"
          },
          {
            "number": "5d",
            "text": "Explain why swimming rescues should not be attempted when a reaching or throwing rescue is possible. Explain why and how a rescue swimmer should avoid contact with the victim."
          }
        ]
      },
      {
        "number": "6",
        "children": [
          {
            "number": "6a",
            "text": "Demonstrate first aid for the following: Object in the eye Bite of a warm blooded animal Puncture wounds from a splinter, nail, and fishhook Serious burns (partial thickness, or second degree) Heat exhaustion Shock Heatstroke, dehydration, hypothermia, and hyperventilation"
          },
          {
            "number": "6b",
            "text": "Show what to do for \"hurry\" cases of stopped breathing, stroke, severe bleeding, and ingested poisoning."
          },
          {
            "number": "6c",
            "text": "Tell what you can do while on a campout or hike to prevent or reduce the occurrence of the injuries listed in Second Class requirements 6a and 6b."
          },
          {
            "number": "6d",
            "text": "Explain what to do in case of accidents that require emergency response in the home and the backcountry. Explain what constitutes an emergency and what information you will need to provide to a responder."
          },
          {
            "number": "6e",
            "text": "Tell how you should respond if you come upon the scene of a vehicular accident."
          }
        ]
      },
      {
        "number": "7",
        "children": [
          {
            "number": "7a",
            "text": "After competing Tenderfoot requirement 6c, be physically active at least 30 minutes a day for five days a week for four weeks. Keep track of your activities."
          },
          {
            "number": "7b",
            "text": "Share your challenges and successes in completing Second Class requirement 7a. Set a goal for continuing to include physical activity as part of your daily life and develop a plan for doing so."
          },
          {
            "number": "7c",
            "text": "Participate in a school, community, or troop program on the dangers of using drugs, alcohol, and tobacco, and other practices that could be harmful to your health. Discuss your participation in the program with your family, and explain the dangers of substance addictions. Report to your Scoutmaster or other adult leader in your troop about which parts of the Scout Oath and Law relate to what you learned."
          }
        ]
      },
      {
        "number": "8",
        "children": [
          {
            "number": "8a",
            "text": "Participate in a flag ceremony for your school, religious institution, chartered organization, community, or Scouting activity."
          },
          {
            "number": "8b",
            "text": "Explain what respect is due the flag of the United States."
          },
          {
            "number": "8c",
            "text": "With your parents or guardian, decide on an amount of money that you would like to earn, based on the cost of a specific item you would like to purchase. Develop a written plan to earn the amount agreed upon and follow that plan; it is acceptable to make changes to your plan along the way. Discuss any changes made to your original plan and whether you met your goal."
          },
          {
            "number": "8d",
            "text": "At a minimum of three locations, compare the cost of the item for which you are saving to determine the best place to purchase it. After completing Second Class requirement 8c, decide if you will use the amount that you earned as originally intended, save all or part of it, or use it for another purpose."
          },
          {
            "number": "8e",
            "text": "Participate in two hours of service through one or more service projects approved by your Scoutmaster. Explain how your service to others relates to the Scout Oath."
          }
        ]
      },
      {
        "number": "9",
        "children": [
          {
            "number": "9a",
            "text": "Explain the three R's of personal safety and protection."
          },
          {
            "number": "9b",
            "text": "Describe bullying; tell what the appropriate response is to someone who is bullying you or another person."
          }
        ]
      },
      {
        "number": "10",
        "text": "Demonstrate scout spirit by living the Scout Oath and Scout Law. Tell how you have done your duty to God and how you have lived four different points of the Scout Law (not to include those used for Tenderfoot requirement 9) in your everyday life."
      },
      {
        "number": "11",
        "text": "While working toward the Second Class rank, and after completing Tenderfoot requirement 10, participate in a Scoutmaster conference."
      },
      {
        "number": "12",
        "text": "Successfully complete your board of review for the Second Class rank."
      }
    ],
    "provenance": {
      "sources": [
        {
          "url": "http://usscouts.org/advance/ScoutsBSA/old/bsrank3.asp"
        },
        {
          "citation": "U.S. Scouting Service Project archived Second Class rank requirements (2018)"
        }
      ],
      "method": "scraped",
      "verified_at": "2026-07-21",
      "confidence": 0.8,
      "notes": "Scraped from usscouts.org archived edition; verbatim requirement text \u00a9 Scouting America, structure/numbering derived; topical section headers omitted."
    },
    "notes": null
  },
  {
    "id": "second-class-2019",
    "kind": "requirement-set",
    "subject": "rank:second-class",
    "effective_from": "2019-01-01",
    "effective_to": "2022-12-31",
    "supersedes": "requirement-set:second-class-2018",
    "source_document": {
      "title": "Second Class Rank Requirements (2019 Boy Scout/Scouts BSA Requirements)",
      "url": "http://usscouts.org/advance/ScoutsBSA/old/rank3-19.asp",
      "year": 2019
    },
    "includes_official_text": true,
    "text_rights": "Requirement text \u00a9 Scouting America, reproduced with attribution for non-commercial Scouting use; NOT licensed under this dataset's CC BY-NC-SA. See NOTICE.md.",
    "requirements": [
      {
        "number": "1",
        "children": [
          {
            "number": "1a",
            "text": "Since joining Scouts BSA, participate in five separate troop/patrol activities, at least three of which must be held outdoors. Of the outdoor activities, at least two must include overnight camping. These activities do not include troop or patrol meetings. On campouts, spend the night in a tent that you pitch or other structure that you help erect, such as a lean-to, snow cave, or tepee."
          },
          {
            "number": "1b",
            "text": "Explain the principles of Leave No Trace, and tell how you practiced them on a campout or outing. This outing must be different from the one used for Tenderfoot requirement 1c."
          },
          {
            "number": "1c",
            "text": "On one of these campouts, select a location for your patrol site and recommend it to your patrol leader, senior patrol leader, or troop guide. Explain what factors you should consider when choosing a patrol site and where to pitch a tent."
          }
        ]
      },
      {
        "number": "2",
        "children": [
          {
            "number": "2a",
            "text": "Explain when it is appropriate to use a fire for cooking or other purposes and when it would not be appropriate to do so."
          },
          {
            "number": "2b",
            "text": "Use the tools listed in Tenderfoot requirement 3d to prepare tinder, kindling, and fuel wood for a cooking fire."
          },
          {
            "number": "2c",
            "text": "At an approved outdoor location and time, use the tinder, kindling, and fuel wood from Second Class requirement 2b to demonstrate how to build a fire. Unless prohibited by local fire restrictions, light the fire. After allowing the flames to burn safely for at least two minutes, safely extinguish the flames with minimal impact to the fire site."
          },
          {
            "number": "2d",
            "text": "Explain when it is appropriate to use a lightweight stove and when it is appropriate to use a propane stove. Set up a lightweight stove or propane stove. Unless prohibited by local fire restrictions, light the stove. Describe the safety procedures for using these types of stoves."
          },
          {
            "number": "2e",
            "text": "On one campout, plan and cook one hot breakfast or lunch, selecting foods from MyPlate or the current USDA nutritional model. Explain the importance of good nutrition. Demonstrate how to transport, store, and prepare the foods you selected."
          },
          {
            "number": "2f",
            "text": "Demonstrate tying the sheet bend knot. Describe a situation in which you would use this knot."
          },
          {
            "number": "2g",
            "text": "Demonstrate tying the bowline knot. Describe a situation in which you would use this knot."
          }
        ]
      },
      {
        "number": "3",
        "children": [
          {
            "number": "3a",
            "text": "Demonstrate how a compass works and how to orient a map. Use a map to point out and tell the meaning of five map symbols."
          },
          {
            "number": "3b",
            "text": "Using a compass and map together, take a five-mile hike (or 10 miles by bike) approved by your adult leader and your parent or guardian. 2"
          },
          {
            "number": "3c",
            "text": "Describe some hazards or injuries that you might encounter on your hike and what you can do to help prevent them. 2"
          },
          {
            "number": "3d",
            "text": "Demonstrate how to find directions during the day and at night without using a compass or an electronic device."
          }
        ]
      },
      {
        "number": "4",
        "text": "Identify or show evidence of at least ten kinds of wild animals (such as birds, mammals, reptiles, fish, mollusks) found in your local area or camping location. You may show evidence by tracks, signs, or photographs you have taken."
      },
      {
        "number": "5",
        "children": [
          {
            "number": "5a",
            "text": "Tell what precautions must be taken for a safe swim."
          },
          {
            "number": "5b",
            "text": "Demonstrate your ability to pass the BSA beginner test. Jump feetfirst into water over your head in depth, level off and swim 25 feet on the surface, stop, turn sharply, resume swimming, then return to your starting place. 3"
          },
          {
            "number": "5c",
            "text": "Demonstrate water rescue methods by reaching with your arm or leg, by reaching with a suitable object, and by throwing lines and objects. 3"
          },
          {
            "number": "5d",
            "text": "Explain why swimming rescues should not be attempted when a reaching or throwing rescue is possible. Explain why and how a rescue swimmer should avoid contact with the victim."
          }
        ]
      },
      {
        "number": "6",
        "children": [
          {
            "number": "6a",
            "text": "Demonstrate first aid for the following: Object in the eye Bite of a warm blooded animal Puncture wounds from a splinter, nail, and fishhook Serious burns (partial thickness, or second degree) Heat exhaustion Shock Heatstroke, dehydration, hypothermia, and hyperventilation"
          },
          {
            "number": "6b",
            "text": "Show what to do for \"hurry\" cases of stopped breathing, stroke, severe bleeding, and ingested poisoning."
          },
          {
            "number": "6c",
            "text": "Tell what you can do while on a campout or hike to prevent or reduce the occurrence of the injuries listed in Second Class requirements 6a and 6b."
          },
          {
            "number": "6d",
            "text": "Explain what to do in case of accidents that require emergency response in the home and the backcountry. Explain what constitutes an emergency and what information you will need to provide to a responder."
          },
          {
            "number": "6e",
            "text": "Tell how you should respond if you come upon the scene of a vehicular accident."
          }
        ]
      },
      {
        "number": "7",
        "children": [
          {
            "number": "7a",
            "text": "After competing Tenderfoot requirement 6c, be physically active at least 30 minutes a day for five days a week for four weeks. Keep track of your activities."
          },
          {
            "number": "7b",
            "text": "Share your challenges and successes in completing Second Class requirement 7a. Set a goal for continuing to include physical activity as part of your daily life and develop a plan for doing so."
          },
          {
            "number": "7c",
            "text": "Participate in a school, community, or troop program on the dangers of using drugs, alcohol, and tobacco, and other practices that could be harmful to your health. Discuss your participation in the program with your family, and explain the dangers of substance addictions. Report to your Scoutmaster or other adult leader in your troop about which parts of the Scout Oath and Law relate to what you learned."
          }
        ]
      },
      {
        "number": "8",
        "children": [
          {
            "number": "8a",
            "text": "Participate in a flag ceremony for your school, religious institution, chartered organization, community, or Scouting activity."
          },
          {
            "number": "8b",
            "text": "Explain what respect is due the flag of the United States."
          },
          {
            "number": "8c",
            "text": "With your parents or guardian, decide on an amount of money that you would like to earn, based on the cost of a specific item you would like to purchase. Develop a written plan to earn the amount agreed upon and follow that plan; it is acceptable to make changes to your plan along the way. Discuss any changes made to your original plan and whether you met your goal."
          },
          {
            "number": "8d",
            "text": "At a minimum of three locations, compare the cost of the item for which you are saving to determine the best place to purchase it. After completing Second Class requirement 8c, decide if you will use the amount that you earned as originally intended, save all or part of it, or use it for another purpose."
          },
          {
            "number": "8e",
            "text": "Participate in two hours of service through one or more service projects approved by your Scoutmaster. Tell how your service to others relates to the Scout Oath."
          }
        ]
      },
      {
        "number": "9",
        "children": [
          {
            "number": "9a",
            "text": "Explain the three R's of personal safety and protection."
          },
          {
            "number": "9b",
            "text": "Describe bullying; tell what the appropriate response is to someone who is bullying you or another person."
          }
        ]
      },
      {
        "number": "10",
        "text": "Demonstrate scout spirit by living the Scout Oath and Scout Law. Tell how you have done your duty to God and how you have lived four different points of the Scout Law (not to include those used for Tenderfoot requirement 9) in your everyday life."
      },
      {
        "number": "11",
        "text": "While working toward the Second Class rank, and after completing Tenderfoot requirement 10, participate in a Scoutmaster conference."
      },
      {
        "number": "12",
        "text": "Successfully complete your board of review for the Second Class rank."
      }
    ],
    "provenance": {
      "sources": [
        {
          "url": "http://usscouts.org/advance/ScoutsBSA/old/rank3-19.asp"
        },
        {
          "citation": "U.S. Scouting Service Project archived Second Class rank requirements (2019)"
        }
      ],
      "method": "scraped",
      "verified_at": "2026-07-21",
      "confidence": 0.8,
      "notes": "Scraped from usscouts.org archived edition; verbatim requirement text \u00a9 Scouting America, structure/numbering derived; topical section headers omitted."
    },
    "notes": null
  },
  {
    "id": "second-class-2023",
    "kind": "requirement-set",
    "subject": "rank:second-class",
    "effective_from": "2023-01-01",
    "effective_to": "2023-12-31",
    "supersedes": "requirement-set:second-class-2019",
    "source_document": {
      "title": "Second Class Rank Requirements (2023 Boy Scout/Scouts BSA Requirements)",
      "url": "http://usscouts.org/advance/ScoutsBSA/old/rank3-23.asp",
      "year": 2023
    },
    "includes_official_text": true,
    "text_rights": "Requirement text \u00a9 Scouting America, reproduced with attribution for non-commercial Scouting use; NOT licensed under this dataset's CC BY-NC-SA. See NOTICE.md.",
    "requirements": [
      {
        "number": "1",
        "children": [
          {
            "number": "1a",
            "text": "Since joining Scouts BSA, participate in five separate troop/patrol activities, at least three of which must be held outdoors. Of the outdoor activities, at least two must include overnight camping. These activities do not include troop or patrol meetings. On campouts, spend the night in a tent that you pitch or other structure that you help erect, such as a lean-to, snow cave, or tepee."
          },
          {
            "number": "1b",
            "text": "Recite the principles of Leave No Trace from memory. Explain how you follow them on all outings."
          },
          {
            "number": "1c",
            "text": "On one of these campouts, select a location for your patrol site and recommend it to your patrol leader, senior patrol leader, or troop guide. Explain what factors you should consider when choosing a patrol site and where to pitch a tent."
          }
        ]
      },
      {
        "number": "2",
        "children": [
          {
            "number": "2a",
            "text": "Explain when it is appropriate to use a fire for cooking or other purposes and when it would not be appropriate to do so."
          },
          {
            "number": "2b",
            "text": "Use a pocketknife, and a saw or axe if needed, to prepare tinder, kindling, and fuel wood for a cooking fire."
          },
          {
            "number": "2c",
            "text": "Using a minimum-impact method, and at an approved outdoor location and time, use the tinder, kindling, and fuel wood from Second Class requirement 2b to demonstrate how to build a fire. Unless prohibited by local fire restrictions, light the fire. After allowing the flames to burn safely for at least two minutes, safely extinguish the flames with minimal impact to the fire site. Properly dispose of the ashes and any charred remains."
          },
          {
            "number": "2d",
            "text": "Explain when it is appropriate to use a lightweight stove and when it is appropriate to use a propane stove. Set up a lightweight stove or propane stove. Unless prohibited by local fire restrictions, light the stove. Describe the safety procedures for using these types of stoves."
          },
          {
            "number": "2e",
            "text": "On one campout, plan and cook one hot breakfast or lunch, selecting foods from MyPlate or the current USDA nutritional model. Explain the importance of good nutrition. Demonstrate how to transport, store, and prepare the foods you selected."
          },
          {
            "number": "2f",
            "text": "Demonstrate tying the sheet bend knot. Describe a situation in which you would use this knot."
          },
          {
            "number": "2g",
            "text": "Demonstrate tying the bowline knot. Describe a situation in which you would use this knot."
          }
        ]
      },
      {
        "number": "3",
        "children": [
          {
            "number": "3a",
            "text": "Demonstrate how a compass works and how to orient a map. Use a map to point out and tell the meaning of five map symbols."
          },
          {
            "number": "3b",
            "text": "Using a compass and map together, take a five-mile hike (or 10 miles by bike) approved by your adult leader and your parent or guardian. 2"
          },
          {
            "number": "3c",
            "text": "Describe some hazards or injuries that you might encounter on your hike and what you can do to help prevent them. 2"
          },
          {
            "number": "3d",
            "text": "Demonstrate how to find directions during the day and at night without using a compass or an electronic device."
          }
        ]
      },
      {
        "number": "4",
        "text": "Identify or show evidence of at least ten kinds of wild animals (such as birds, mammals, reptiles, fish, mollusks) found in your local area or camping location. You may show evidence by tracks, signs, or photographs you have taken."
      },
      {
        "number": "5",
        "children": [
          {
            "number": "5a",
            "text": "Tell what precautions must be taken for a safe swim."
          },
          {
            "number": "5b",
            "text": "Demonstrate your ability to pass the BSA beginner test. Jump feetfirst into water over your head in depth, level off and swim 25 feet on the surface, stop, turn sharply, resume swimming, then return to your starting place. 3"
          },
          {
            "number": "5c",
            "text": "Demonstrate water rescue methods by reaching with your arm or leg, by reaching with a suitable object, and by throwing lines and objects. 3"
          },
          {
            "number": "5d",
            "text": "Explain why swimming rescues should not be attempted when a reaching or throwing rescue is possible. Explain why and how a rescue swimmer should avoid contact with the victim."
          }
        ]
      },
      {
        "number": "6",
        "children": [
          {
            "number": "6a",
            "text": "Demonstrate first aid for the following: Object in the eye Bite of a warm blooded animal Puncture wounds from a splinter, nail, and fishhook Serious burns (partial thickness, or second degree) Heat exhaustion Shock Heatstroke, dehydration, hypothermia, and hyperventilation"
          },
          {
            "number": "6b",
            "text": "Show what to do for \"hurry\" cases of stopped breathing, stroke, severe bleeding, and ingested poisoning."
          },
          {
            "number": "6c",
            "text": "Tell what you can do while on a campout or hike to prevent or reduce the occurrence of the injuries listed in Second Class requirements 6a and 6b."
          },
          {
            "number": "6d",
            "text": "Explain what to do in case of accidents that require emergency response in the home and the backcountry. Explain what constitutes an emergency and what information you will need to provide to a responder."
          },
          {
            "number": "6e",
            "text": "Tell how you should respond if you come upon the scene of a vehicular accident."
          }
        ]
      },
      {
        "number": "7",
        "children": [
          {
            "number": "7a",
            "text": "After competing Tenderfoot requirement 6c, be physically active at least 30 minutes a day for five days a week for four weeks. Keep track of your activities."
          },
          {
            "number": "7b",
            "text": "Share your challenges and successes in completing Second Class requirement 7a. Set a goal for continuing to include physical activity as part of your daily life and develop a plan for doing so."
          },
          {
            "number": "7c",
            "text": "Participate in a school, community, or troop program on the dangers of using drugs, alcohol, and tobacco, and other practices that could be harmful to your health. Discuss your participation in the program with your family, and explain the dangers of substance addictions. Report to your Scoutmaster or other adult leader in your troop about which parts of the Scout Oath and Law relate to what you learned."
          }
        ]
      },
      {
        "number": "8",
        "children": [
          {
            "number": "8a",
            "text": "Participate in a flag ceremony for your school, religious institution, chartered organization, community, or Scouting activity."
          },
          {
            "number": "8b",
            "text": "Explain what respect is due the flag of the United States."
          },
          {
            "number": "8c",
            "text": "With your parents or guardian, decide on an amount of money that you would like to earn, based on the cost of a specific item you would like to purchase. Develop a written plan to earn the amount agreed upon and follow that plan; it is acceptable to make changes to your plan along the way. Discuss any changes made to your original plan and whether you met your goal."
          },
          {
            "number": "8d",
            "text": "At a minimum of three locations, compare the cost of the item for which you are saving to determine the best place to purchase it. After completing Second Class requirement 8c, decide if you will use the amount that you earned as originally intended, save all or part of it, or use it for another purpose."
          },
          {
            "number": "8e",
            "text": "Participate in two hours of service through one or more service projects approved by your Scoutmaster. Tell how your service to others relates to the Scout Oath."
          }
        ]
      },
      {
        "number": "9",
        "children": [
          {
            "number": "9a",
            "text": "Explain the three R's of personal safety and protection."
          },
          {
            "number": "9b",
            "text": "Describe bullying; tell what the appropriate response is to someone who is bullying you or another person."
          }
        ]
      },
      {
        "number": "10",
        "text": "Demonstrate scout spirit by living the Scout Oath and Scout Law. Tell how you have done your duty to God and how you have lived four different points of the Scout Law (not to include those used for Tenderfoot requirement 9) in your everyday life."
      },
      {
        "number": "11",
        "text": "While working toward the Second Class rank, and after completing Tenderfoot requirement 10, participate in a Scoutmaster conference."
      },
      {
        "number": "12",
        "text": "Successfully complete your board of review for the Second Class rank."
      }
    ],
    "provenance": {
      "sources": [
        {
          "url": "http://usscouts.org/advance/ScoutsBSA/old/rank3-23.asp"
        },
        {
          "citation": "U.S. Scouting Service Project archived Second Class rank requirements (2023)"
        }
      ],
      "method": "scraped",
      "verified_at": "2026-07-21",
      "confidence": 0.8,
      "notes": "Scraped from usscouts.org archived edition; verbatim requirement text \u00a9 Scouting America, structure/numbering derived; topical section headers omitted."
    },
    "notes": null
  },
  {
    "id": "star-2016",
    "kind": "requirement-set",
    "subject": "rank:star",
    "effective_from": "2016-01-01",
    "effective_to": "2017-12-31",
    "supersedes": null,
    "source_document": {
      "title": "Star Rank Requirements (2016 Boy Scout/Scouts BSA Requirements)",
      "url": "http://usscouts.org/advance/boyscout/old/bsrank5-16.asp",
      "year": 2016
    },
    "includes_official_text": true,
    "text_rights": "Requirement text \u00a9 Scouting America, reproduced with attribution for non-commercial Scouting use; NOT licensed under this dataset's CC BY-NC-SA. See NOTICE.md.",
    "requirements": [
      {
        "number": "1",
        "text": "Be active in your troop for at least four months as a First Class Scout."
      },
      {
        "number": "2",
        "text": "As a First Class Scout, demonstrate Scout spirit by living the Scout Oath and Scout Law. Tell how you have done your duty to God and how you have lived the Scout Oath and Scout Law in your everyday life."
      },
      {
        "number": "3",
        "text": "Earn six merit badges, including any four from the required list for Eagle . You may choose any of the 17 merit badges on the required list for Eagle to fulfill this requirement. See Eagle rank requirement 3 for this list. Name of Merit Badge Date Earned (Eagle required) _________________________ _________________________ (Eagle required) _________________________ _________________________ (Eagle required) _________________________ _________________________ (Eagle required) _________________________ _________________________ _________________________ _________________________ _________________________ _________________________"
      },
      {
        "number": "4",
        "text": "While a First Class Scout, participate in six hours of service through one or more service projects approved by your Scoutmaster."
      },
      {
        "number": "5",
        "text": "While a First Class Scout, serve actively in your troop for four months in one or more of the following positions of responsibility (or carry out a Scoutmaster assigned leadership project to help the troop): Boy Scout troop. Patrol leader, assistant senior patrol leader, senior patrol leader, troop guide, Order of the Arrow troop representative, den chief, scribe, librarian, historian, quartermaster, bugler, junior assistant Scoutmaster, chaplain aide, instructor, webmaster, or outdoor ethics guide 4 Varsity Scout team. Captain, co-captain, program manager, squad leader, team secretary, Order of the Arrow team representative, librarian, historian, quartermaster, chaplain aide, instructor, den chief, webmaster, or outdoor ethics guide Venturing crew / Sea Scout ship. President, vice president, secretary, treasurer, den chief, quartermaster, historian, guide, boatswain, boatswain's mate, yeoman, purser, storekeeper, or webmaster, Lone Scout. Leadership responsibility in your school, religious organization, club, or elsewhere in your community."
      },
      {
        "number": "6",
        "text": "With your parent or guardian, complete the exercises in the pamphlet \"How to Protect Your Children from Child Abuse: A Parents Guide\" and earn the Cyber Chip Award for your grade. 5"
      },
      {
        "number": "7",
        "text": "While a First Class Scout, participate in a Scoutmaster conference"
      },
      {
        "number": "8",
        "text": "Successfully complete your board of review for the Star rank. 6"
      }
    ],
    "provenance": {
      "sources": [
        {
          "url": "http://usscouts.org/advance/boyscout/old/bsrank5-16.asp"
        },
        {
          "citation": "U.S. Scouting Service Project archived Star rank requirements (2016)"
        }
      ],
      "method": "scraped",
      "verified_at": "2026-07-21",
      "confidence": 0.8,
      "notes": "Scraped from usscouts.org archived edition; verbatim requirement text \u00a9 Scouting America, structure/numbering derived; topical section headers omitted."
    },
    "notes": null
  },
  {
    "id": "star-2018",
    "kind": "requirement-set",
    "subject": "rank:star",
    "effective_from": "2018-01-01",
    "effective_to": "2020-12-31",
    "supersedes": "requirement-set:star-2016",
    "source_document": {
      "title": "Star Rank Requirements (2018 Boy Scout/Scouts BSA Requirements)",
      "url": "http://usscouts.org/advance/ScoutsBSA/old/bsrank5.asp",
      "year": 2018
    },
    "includes_official_text": true,
    "text_rights": "Requirement text \u00a9 Scouting America, reproduced with attribution for non-commercial Scouting use; NOT licensed under this dataset's CC BY-NC-SA. See NOTICE.md.",
    "requirements": [
      {
        "number": "1",
        "text": "Be active in your troop for at least four months as a First Class Scout."
      },
      {
        "number": "2",
        "text": "As a First Class Scout, demonstrate Scout spirit by living the Scout Oath and Scout Law. Tell how you have done your duty to God and how you have lived the Scout Oath and Scout Law in your everyday life."
      },
      {
        "number": "3",
        "text": "Earn six merit badges, including any four from the required list for Eagle . You may choose any of the 17 merit badges on the required list for Eagle to fulfill this requirement. See Eagle rank requirement 3 for this list. Name of Merit Badge Date Earned (Eagle required) _________________________ _________________________ (Eagle required) _________________________ _________________________ (Eagle required) _________________________ _________________________ (Eagle required) _________________________ _________________________ _________________________ _________________________ _________________________ _________________________"
      },
      {
        "number": "4",
        "text": "While a First Class Scout, participate in six hours of service through one or more service projects approved by your Scoutmaster."
      },
      {
        "number": "5",
        "text": "While a First Class Scout, serve actively in your troop for four months in one or more of the following positions of responsibility (or carry out a Scoutmaster assigned leadership project to help the troop): Boy Scout troop. Patrol leader, assistant senior patrol leader, senior patrol leader, troop guide, Order of the Arrow troop representative, den chief, scribe, librarian, historian, quartermaster, bugler, junior assistant Scoutmaster, chaplain aide, instructor, webmaster, or outdoor ethics guide 6 Venturing crew President, vice president, secretary, treasurer, den chief, historian, guide, quartermaster, chaplain aide, or outdoor ethics guide Sea Scout ship. boatswain, boatswain's mate, purser, yeoman, storekeeper, or crew leader, media specialist, specialist, den chief, or chaplain aide. Lone Scout. Leadership responsibility in your school, religious organization, club, or elsewhere in your community."
      },
      {
        "number": "6",
        "text": "With your parent or guardian, complete the exercises in the pamphlet \" How to Protect Your Children from Child Abuse: A Parents Guid e\" and earn the Cyber Chip Award for your grade. 7"
      },
      {
        "number": "7",
        "text": "While a First Class Scout, participate in a Scoutmaster conference"
      },
      {
        "number": "8",
        "text": "Successfully complete your board of review for the Star rank. 8"
      }
    ],
    "provenance": {
      "sources": [
        {
          "url": "http://usscouts.org/advance/ScoutsBSA/old/bsrank5.asp"
        },
        {
          "citation": "U.S. Scouting Service Project archived Star rank requirements (2018)"
        }
      ],
      "method": "scraped",
      "verified_at": "2026-07-21",
      "confidence": 0.8,
      "notes": "Scraped from usscouts.org archived edition; verbatim requirement text \u00a9 Scouting America, structure/numbering derived; topical section headers omitted."
    },
    "notes": null
  },
  {
    "id": "star-2021",
    "kind": "requirement-set",
    "subject": "rank:star",
    "effective_from": "2021-01-01",
    "effective_to": "2022-12-31",
    "supersedes": "requirement-set:star-2018",
    "source_document": {
      "title": "Star Rank Requirements (2021 Boy Scout/Scouts BSA Requirements)",
      "url": "http://usscouts.org/advance/ScoutsBSA/old/rank5-21.asp",
      "year": 2021
    },
    "includes_official_text": true,
    "text_rights": "Requirement text \u00a9 Scouting America, reproduced with attribution for non-commercial Scouting use; NOT licensed under this dataset's CC BY-NC-SA. See NOTICE.md.",
    "requirements": [
      {
        "number": "1",
        "text": "Be active in your troop for at least four months as a First Class Scout."
      },
      {
        "number": "2",
        "text": "As a First Class Scout, demonstrate Scout spirit by living the Scout Oath and Scout Law. Tell how you have done your duty to God and how you have lived the Scout Oath and Scout Law in your everyday life."
      },
      {
        "number": "3",
        "text": "Earn six merit badges, including any four from the required list for Eagle . You may choose any of the 17 merit badges on the required list for Eagle to fulfill this requirement. See Eagle rank requirement 3 for this list."
      },
      {
        "number": "4",
        "text": "While a First Class Scout, participate in six hours of service through one or more service projects approved by your Scoutmaster."
      },
      {
        "number": "5",
        "text": "While a First Class Scout, serve actively in your troop for four months in one or more of the following positions of responsibility (or carry out a Scoutmaster assigned leadership project to help the troop): Scout troop. Patrol leader, assistant senior patrol leader, senior patrol leader, troop guide, Order of the Arrow troop representative, den chief, scribe, librarian, historian, quartermaster, bugler, junior assistant Scoutmaster, chaplain aide, instructor, webmaster, or outdoor ethics guide 6 Venturing crew President, vice president, secretary, treasurer, den chief, historian, guide, quartermaster, chaplain aide, or outdoor ethics guide Sea Scout ship. boatswain, boatswain's mate, purser, yeoman, storekeeper, or crew leader, media specialist, specialist, den chief, or chaplain aide. Lone Scout. Leadership responsibility in your school, religious organization, club, or elsewhere in your community."
      },
      {
        "number": "6",
        "text": "With your parent or guardian, complete the exercises in the pamphlet \" How to Protect Your Children from Child Abuse: A Parents Guid e\" and earn the Cyber Chip Award for your grade. 7"
      },
      {
        "number": "7",
        "text": "While a First Class Scout, participate in a Scoutmaster conference"
      },
      {
        "number": "8",
        "text": "Successfully complete your board of review for the Star rank. 8"
      }
    ],
    "provenance": {
      "sources": [
        {
          "url": "http://usscouts.org/advance/ScoutsBSA/old/rank5-21.asp"
        },
        {
          "citation": "U.S. Scouting Service Project archived Star rank requirements (2021)"
        }
      ],
      "method": "scraped",
      "verified_at": "2026-07-21",
      "confidence": 0.8,
      "notes": "Scraped from usscouts.org archived edition; verbatim requirement text \u00a9 Scouting America, structure/numbering derived; topical section headers omitted."
    },
    "notes": null
  },
  {
    "id": "star-2023",
    "kind": "requirement-set",
    "subject": "rank:star",
    "effective_from": "2023-01-01",
    "effective_to": "2023-12-31",
    "supersedes": "requirement-set:star-2021",
    "source_document": {
      "title": "Star Rank Requirements (2023 Boy Scout/Scouts BSA Requirements)",
      "url": "http://usscouts.org/advance/ScoutsBSA/old/rank5-23.asp",
      "year": 2023
    },
    "includes_official_text": true,
    "text_rights": "Requirement text \u00a9 Scouting America, reproduced with attribution for non-commercial Scouting use; NOT licensed under this dataset's CC BY-NC-SA. See NOTICE.md.",
    "requirements": [
      {
        "number": "1",
        "text": "Be active in your troop for at least four months as a First Class Scout."
      },
      {
        "number": "2",
        "text": "As a First Class Scout, demonstrate Scout spirit by living the Scout Oath and Scout Law. Tell how you have done your duty to God and how you have lived the Scout Oath and Scout Law in your everyday life."
      },
      {
        "number": "3",
        "text": "Earn six merit badges, including any four from the required list for Eagle . You may choose any of the merit badges on the required list for Eagle to fulfill this requirement. See Eagle rank requirement 3 for this list."
      },
      {
        "number": "4",
        "text": "While a First Class Scout, participate in six hours of service through one or more service projects approved by your Scoutmaster."
      },
      {
        "number": "5",
        "text": "While a First Class Scout, serve actively in your troop for four months in one or more of the following positions of responsibility (or carry out a Scoutmaster assigned leadership project to help the troop): Scout troop. Patrol leader, assistant senior patrol leader, senior patrol leader, troop guide, Order of the Arrow troop representative, den chief, scribe, librarian, historian, quartermaster, bugler, junior assistant Scoutmaster, chaplain aide, instructor, webmaster, or outdoor ethics guide 6 Venturing crew President, vice president, secretary, treasurer, den chief, historian, guide, quartermaster, chaplain aide, or outdoor ethics guide Sea Scout ship. boatswain, boatswain's mate, purser, yeoman, storekeeper, or crew leader, media specialist, specialist, den chief, or chaplain aide. Lone Scout. Leadership responsibility in your school, religious organization, club, or elsewhere in your community."
      },
      {
        "number": "6",
        "text": "With your parent or guardian, complete the exercises in the pamphlet \" How to Protect Your Children from Child Abuse: A Parents Guid e\" and earn the Cyber Chip Award for your grade or view the Personal Safety Awareness videos ( with your parent or Guardian's permission). 7"
      },
      {
        "number": "7",
        "text": "While a First Class Scout, participate in a Scoutmaster conference"
      },
      {
        "number": "8",
        "text": "Successfully complete your board of review for the Star rank. 8"
      }
    ],
    "provenance": {
      "sources": [
        {
          "url": "http://usscouts.org/advance/ScoutsBSA/old/rank5-23.asp"
        },
        {
          "citation": "U.S. Scouting Service Project archived Star rank requirements (2023)"
        }
      ],
      "method": "scraped",
      "verified_at": "2026-07-21",
      "confidence": 0.8,
      "notes": "Scraped from usscouts.org archived edition; verbatim requirement text \u00a9 Scouting America, structure/numbering derived; topical section headers omitted."
    },
    "notes": null
  },
  {
    "id": "tenderfoot-2016",
    "kind": "requirement-set",
    "subject": "rank:tenderfoot",
    "effective_from": "2016-01-01",
    "effective_to": "2023-12-31",
    "supersedes": null,
    "source_document": {
      "title": "Tenderfoot Rank Requirements (2016 Boy Scout/Scouts BSA Requirements)",
      "url": "http://usscouts.org/advance/boyscout/old/bsrank2-16.asp",
      "year": 2016
    },
    "includes_official_text": true,
    "text_rights": "Requirement text \u00a9 Scouting America, reproduced with attribution for non-commercial Scouting use; NOT licensed under this dataset's CC BY-NC-SA. See NOTICE.md.",
    "requirements": [
      {
        "number": "1",
        "children": [
          {
            "number": "1a",
            "text": "Present yourself to your leader prepared for an overnight camping trip. Show the personal and camping gear you will use. Show the right way to pack and carry it."
          },
          {
            "number": "1b",
            "text": "Spend at least one night on a patrol or troop campout. Sleep in a tent you have helped pitch."
          },
          {
            "number": "1c",
            "text": "Tell how you practiced the Outdoor Code on a campout or outing."
          }
        ]
      },
      {
        "number": "2",
        "children": [
          {
            "number": "2a",
            "text": "On the campout, assist in preparing one of the meals. Tell why it is important for each patrol member to share in meal preparation and cleanup."
          },
          {
            "number": "2b",
            "text": "While on a campout, demonstrate the appropriate method of safely cleaning items used to prepare, serve, and eat a meal."
          },
          {
            "number": "2c",
            "text": "Explain the importance of eating together as a patrol."
          }
        ]
      },
      {
        "number": "3",
        "children": [
          {
            "number": "3a",
            "text": "Demonstrate a practical use of the square knot."
          },
          {
            "number": "3b",
            "text": "Demonstrate a practical use of two half-hitches."
          },
          {
            "number": "3c",
            "text": "Demonstrate a practical use of the taut line hitch."
          },
          {
            "number": "3d",
            "text": "Demonstrate proper care, sharpening, and use of the knife, saw, and ax. Describe when each should be used."
          }
        ]
      },
      {
        "number": "4",
        "children": [
          {
            "number": "4a",
            "text": "Show first aid for the following: Simple cuts and scrapes Blisters on the hand and foot Minor (thermal/heat) burns or scalds (superficial, or first degree) Bites or stings of insects or ticks Venomous snakebite Nosebleed Frostbite and sunburn Choking"
          },
          {
            "number": "4b",
            "text": "Describe common poisonous or hazardous plants, identify any that grow in your local area or campsite location. Tell how to treat for exposure to them."
          },
          {
            "number": "4c",
            "text": "Tell what you can do on a campout or other outdoor activity to prevent or reduce the occurrence of injuries or exposure listed in Tenderfoot requirements 4a and 4b."
          },
          {
            "number": "4d",
            "text": "Assemble a personal first-aid kit to carry with you on future campouts and hikes. Tell how each item in the kit would be used."
          }
        ]
      },
      {
        "number": "5",
        "children": [
          {
            "number": "5a",
            "text": "Explain the importance of the buddy system as it relates to your personal safety on outings and in your neighborhood. Use the buddy system while on a troop or patrol outing."
          },
          {
            "number": "5b",
            "text": "Explain what to do if you become lost on a hike or campout."
          },
          {
            "number": "5c",
            "text": "Explain the rules of safe hiking, both on the highway and cross-country, during the day and at night."
          }
        ]
      },
      {
        "number": "6",
        "children": [
          {
            "number": "6a",
            "text": "Record your best in the following tests: \u2022 Pushups ________ (Record the number done correctly in 60 seconds) \u2022 Situps or curl-ups ________ (Record the number done correctly in 60 seconds) \u2022 Back-saver sit-and-reach ________ (Record the distance stretched) \u2022 1 mile walk/run ________ (Record the time)"
          },
          {
            "number": "6b",
            "text": "Develop and describe a plan for improvement in each of the activities listed in Tenderfoot requirement 6a. Keep track of your activity for at least 30 days."
          },
          {
            "number": "6c",
            "text": "Show improvement (of any degree) in each activity listed in Tenderfoot requirement 6a after practicing for 30 days. \u2022 Pushups ________ (Record the number done correctly in 60 seconds) \u2022 Situps or curl-ups ________ (Record the number done correctly in 60 seconds) \u2022 Back-saver sit-and-reach ________ (Record the distance stretched) \u2022 1 mile walk/run ________ (Record the time)"
          }
        ]
      },
      {
        "number": "7",
        "children": [
          {
            "number": "7a",
            "text": "Demonstrate how to display, raise, lower, and fold the U.S. flag."
          },
          {
            "number": "7b",
            "text": "Participate in a total of one hour of service in one or more service projects approved by your Scoutmaster. Explain how your service to others relates to the Scout slogan and Scout motto."
          }
        ]
      },
      {
        "number": "8",
        "text": "Describe the steps in Scouting's Teaching EDGE method. Use the Teaching EDGE method to teach another person how to tie the square knot."
      },
      {
        "number": "9",
        "text": "Demonstrate Scout spirit by living the Scout Oath and Scout Law. Tell how you have done your duty to God and how you have lived four different points of the Scout Law in your everyday life."
      },
      {
        "number": "10",
        "text": "While working toward Tenderfoot rank, and after completing Scout rank requirement 7, participate in a Scoutmaster conference."
      },
      {
        "number": "11",
        "text": "Successfully complete your board of review for the Tenderfoot rank."
      }
    ],
    "provenance": {
      "sources": [
        {
          "url": "http://usscouts.org/advance/boyscout/old/bsrank2-16.asp"
        },
        {
          "citation": "U.S. Scouting Service Project archived Tenderfoot rank requirements (2016)"
        }
      ],
      "method": "scraped",
      "verified_at": "2026-07-21",
      "confidence": 0.8,
      "notes": "Scraped from usscouts.org archived edition; verbatim requirement text \u00a9 Scouting America, structure/numbering derived; topical section headers omitted."
    },
    "notes": null
  }
]
""")


def main() -> None:
    out_dir = Path(__file__).resolve().parents[1] / "data" / "requirement-sets"
    out_dir.mkdir(parents=True, exist_ok=True)
    for doc in DOCS:
        (out_dir / f"{doc['id']}.json").write_text(
            json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"historical rank requirement-sets: {len(DOCS)} documents written")


if __name__ == "__main__":
    main()

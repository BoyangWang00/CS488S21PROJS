# CS488: Computer Networks and The Internet
[Pace University](http://www.pace.edu)

Instructor: [Dr. Jun Yuan](http://csis.pace.edu/~jyuan2/)

**The content of this course changes as technology evolves**, to keep up to date with changes [follow me on GitHub](https://github.com/jyuan2pace/CS488S21).

* Section 20882. Spring 2021, Tuesday & Thursday, 12:15 PM, [Zoom meeting link](https://pace.zoom.us/j/6313313504?pwd=bUJtV3NUUlBiZVNKTThTRHBoMi84Zz09) 

# Course Description

This course provides a top-down study of modern computer networking and the Internet. Application layer topics include the Web, HTTP, FTP, SMTP, DNS, and socket programming. Transport layer topics include UDP, TCP, and congestion control. Network layer topics include link state routing, distance vector routing, IPv4, RIP, OSPF, BGP, IPv6, multicasting and IGMP, and mobile IP. Local area network topics include Ethernet, IEEE, 802.11, and Bluetooth.

# Textbook

* **[Required]**  Computer Networking: A Top-Down Approach, By James F. Kurose; Keith W. Ross. Edition: 6,  ISBN:9780132856201
* **[Recommended]** TCP/IP Illustrated, Vol. 1: The Protocols; By Richard Steves. ISBN: 978-0201633467

# Objectives

1. Understand the fundamental concepts of computer networks, particularly as related to the Internet;
2. Understand the multi-layer model of modern network architecture and its advantages and complexities;
3. Understand application layer messages and protocols, and write application layer software using sockets;
4. Understand transport layer functionality and explain how congestion control is implemented on the Internet;
5. Understand inter-networking and network layer functionality, and explain how routing is implemented on the Internet and network management;
6. Understand local area networks and link-layer issues including the details of the Ethernet and
IEEE 802.11 protocols;
7. Demonstrate your understanding of the material through a final project uploaded to GitHub.

# Syllabus
This syllabus presents the expected class schedule, due dates, and reading assignments.  [Check current syllabus.](https://docs.google.com/document/d/1xm9FhonUHEuMwYttbQLTa5kgFB2k3s4wz1XRF6_BUy4/edit?usp=sharing)

# Live Schedule
Week|Content|Recording|Reading|Quiz|Deadline
---|---|---|---|---|---
Week 1: <br>Slides [1-1](https://kami.app/p3ZfF70lkGKY) and [1-2](https://kami.app/eIjkbz8Kfdb1)<br>First class on 01/26/2021 | **Week 1: Course Intro and Logistics** <ul><li>Part 1.1: Admin and Logistics <li>Part 1.2: Internet history and overview <li>Part 1.3: Network Arch <li>Part 1.4: Design problems</ul> |<ul><li>[Logistics and overview](https://pace.hosted.panopto.com/Panopto/Pages/Viewer.aspx?id=4dfd3c6d-022b-422d-aa56-acbc01592d72) <li> [Network arch and layering design](https://pace.hosted.panopto.com/Panopto/Pages/Viewer.aspx?id=85618b27-3616-4725-a64c-acbe015ac6f4) </ul>|<ul> <li> [Syllabus](https://docs.google.com/document/d/1xm9FhonUHEuMwYttbQLTa5kgFB2k3s4wz1XRF6_BUy4/edit?usp=sharing) <li>Chapter 1.1-1.2, 1.5, 1.7 <li>[Evolution of the TCP/IP stack(including the embeded 3min33s interview with Bob Khan)](http://som.csudh.edu/fac/lpress/471/hout/tcpiphist.htm)</ul>| Quiz#1 is out on Gradescope | Quiz#1 due 01/31/2021 
Week 2:<br>[Adds-on to week1](https://kami.app/q0LBp6YJ0VqW)<br>Week of 02/02/2021 | **Week 2: Python Prelimaries** <ul><li>	Part 2.1: Review quiz and layering <li>	Part 2.2: Packet switching <li>	Part 2.3: Network measurements <li>	Part 2.4: Variable declaration and assignment <li>Part 2.5: Integers, reals, mathematical operations on different numeric types<li>Part 2.6: Basic strings </ul> |<ul><li>[2-1 Wrapping up networking overview](https://pace.hosted.panopto.com/Panopto/Pages/Viewer.aspx?id=42d11e0c-4db3-48f2-abb2-acc4008478a2) <li> [2-2. Intro to Python](https://pace.hosted.panopto.com/Panopto/Pages/Viewer.aspx?id=81bd067b-8681-4bf8-81e0-acc50158366f) </ul>|<ul>Finalized reading list: <li>[Watch: How Packet Travels in Network](https://www.youtube.com/watch?v=xIuBmOufbls)<li>[Chapter 2 from Think Python](http://www.greenteapress.com/thinkpython/html/thinkpython003.html) <li>[Numbers from the Python Tutorial](https://docs.python.org/3.4/tutorial/introduction.html#numbers)<li>To be moved to next week:[Read the while and break statements from Think Python](http://www.greenteapress.com/thinkpython/html/thinkpython008.html#toc79)</ul>|Quiz#2 is on Gradescope | Quiz#2 due 02/07/2021 
Week 3:<br>[Notes](https://colab.research.google.com/drive/1DGjoeOFKo9LTWmEwVvj-Rk_FjRGxvPug?usp=sharing)<br>Week of 02/09/2021 | **Week 3: Dive into Python** <ul> <li>Part 3.1: Review IO, mathematical operations on different numeric types<li>Part 3.2: Conditions <li>Part 3.3: Loops <li>Part 3.4: Lists <li>Part 3.5: Functions <li>Part 3.5: Strings </ul> |<ul><li>[3-1. Python basics](https://pace.hosted.panopto.com/Panopto/Pages/Viewer.aspx?id=9507e6b6-2836-453d-a99f-acca016c239e) <li> [3-2. Python basics 2](https://pace.hosted.panopto.com/Panopto/Pages/Viewer.aspx?id=03505f2a-24f9-49d5-b587-accc0168c1bb) </ul>|<ul>Finalized Reading list: <li>[Read the while and break statements from Think Python](http://www.greenteapress.com/thinkpython/html/thinkpython008.html#toc79)<li>[Learn python 3 **beginner** 1-4 and 6](./python_materials/learn-python3): complete the notebooks first then do exercises </ul>|Quiz#3 is out on Gradescope | Quiz#3 due 02/14/2021 

# Hands-out
* [Python 3 Cheating Sheet](./python_materials/python3cheatsheet.pdf)
* [Virtualize Python Execution](http://www.pythontutor.com/visualize.html#mode=edit)

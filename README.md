# bupt-api

北邮的一些api

## 使用

``` python
from bupt_api.jwxt import Jwxt
jwxt = Jwxt(username,password) //信息门户的那个
jwxt.get_classes() // 获得课程信息
```

## TODO

- [ ] jwxt 获取不及格信息

- [ ] jwxt 抢课脚本

- [ ] my 获取今天，明天课表

  .......

## 文档

### My  服务门户

#### function

1. my.get_lecture()  
   * 最新一页的讲座信息
   * 输入：无
   * 输出：List[[Lecture](#Lecture)]
2. my.get_after_lecture()
   * 还未开始的讲座信息
   * 输入： 无
   * 输出： List[[Lecture](#Lecture)]
3. my.get_money_info() 
   * 获取北邮通的余额
   * 输入：无
   * 输出： float
4. my.get_book_info() 
   * 获取借阅信息
   * 输入：无
   * 输出： str

#### dataclass

1. <span id="Lecture">Lecture</span>

   | 字段 | 类别              | 注释         |
   | ---- | ----------------- | ------------ |
   | name | str               | 讲座名称     |
   | url  | str               | 讲座内容链接 |
   | time | datatime.datetime | 讲座时间     |

### Jwxt 教务系统

#### function

1. jwxt.get_pass_score()
   * 获得已通过的成绩
   * 输入： 无
   * 输出： List[[Term](#Term)]
2. jwxt.get_classes()
   * 获得当前课表
   * 输入：无
   * 输出：List[[Class](#Class)]

#### dataclass

1. <span id="Term">Term</span>

| 字段   | 类别                            | 注释           |
| ------ | ------------------------------- | -------------- |
| name   | str                             | 学期名称       |
| class_ | List[[ClassScore](#ClassScore)] | 当前学期的成绩 |

2.  <span id="ClassScore">ClassScore</span>

| 字段        | 类别  | 注释       |
| ----------- | ----- | ---------- |
| number      | str   | 课程号     |
| sort_number | str   | 课序号     |
| name        | str   | 课程名     |
| eng_name    | str   | 英文课程名 |
| credit      | float | 学分       |
| score       | float | 成绩       |
| attr        | str   | 课程属性   |

3.  <span id="Class"> Class </span>

| 字段     | 类别                          | 注释           |
| -------- | ----------------------------- | -------------- |
| name     | str                           | 课程名         |
| teacher  | str                           | 授课老师       |
| location | str                           | 上课地点       |
| weekday  | int                           | 周几上课       |
| weeks    | str                           | 第几周上课     |
| session  | int                           | 上课节数       |
| number   | int                           | 第几节开始上课 |
| time     | List[[ClassTime](#ClassTime)] | 上课时间       |

4. <span id="ClassTime">ClassTime</span>

| 字段       | 类别              | 注释     |
| ---------- | ----------------- | -------- |
| start_time | datetime.datetime | 开始时间 |
| end_time   | datetime.datetime | 结束时间 |

### Card 学生卡（北邮通）

#### function

1. get_costs(start_time, end_time)
   * 拿到一定时间内的消费记录
   * 输入
     1. start_time : str 开始时间
     2. end_time : str 结束时间
   * 输出 List[[Cost](#Cost)]

#### dataclass

1. <span id="Cost">Cost</span>

| 字段     | 类别  | 注释     |
| -------- | ----- | -------- |
| time     | str   | 消费时间 |
| desc     | str   | 消费描述 |
| cost     | float | 消费金额 |
| balance  | float | 账户余额 |
| location | str   | 消费地点 |
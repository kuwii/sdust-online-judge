# 用户端API

## 个人

* 登录/注销

```
/api/login/
/api/logout/
```

* 个人信息

```
/api/personal/{username}/  （读|改）
```

* 修改密码

```
/api/password/{username}/  （改）
```

## 全局管理API

### 用户管理

#### 超级管理员

```
/api-admin/roots/
/api-admin/roots/{username}/
```

#### 全局管理员

```
/api-admin/admins/
/api-admin/admins/{username}/
```

#### 用户管理员

```
/api-admin/user-admins/
/api-admin/user-admins/{username}/
```

#### 机构管理员

```
/api-admin/org-admins/
/api-admin/org-admins/{username}/
```

#### 用户

```
/api-admin/users/
/api-admin/users/{username}/
```

### 机构管理

#### 机构

* 机构

```
/api-admin/organizations/
/api-admin/organizations/{oid}/
```

* 机构使用的题库

```
/api-admin/organizations/{oid}/categories/
```

* 机构可使用的题库

```
/api-admin/organizations/{oid}/available-categories/
```

#### 机构内教务管理员

```
/api-admin/organizations/{oid}/admins/
/api-admin/organizations/{oid}/admins/{eid}/
```

## 机构内事务API

### 用户管理

#### 教务管理员

```
/api/organizations/{oid}/admins/ 只读
/api-admin/organizations/{oid}/admins/{eid}/ 只读
```

#### 教师

```
/api/organizations/teachers/
/api/organizations/teachers/{tid}/
```

#### 学生

```
/api/organizations/students/
/api/organizations/students/{sid}/
```

### 课程管理

#### 课程基类

* 课程基类

    ```
    /api/organizations/{oid}/course-meta/
    /api/course-meta/{mid}/
    ```

* 课程基类下的课程与课程组

    ```
    /api/course-meta/{mid}/courses/
    /api/course-meta/{mid}/course-groups/
    ```
    
* 课程基类下的任务

    ```
    /api/course-meta/{mid}/missions/
    ```
    
* 课程基类下的题库

    已添加的题库

    ```
    /api/course-meta/{mid}/categories/
    ```
    
    可添加的题库
    
    ```
    /api/course-meta/{mid}/available-categories/
    ```

#### 课程

* 课程

    ```
    /api/teaching-courses/  （只读）
    /api/learning-courses/  （只读）
    /api/courses/{cid}/     （只读）
    ```
    
* 课程下教师

    ```
    /api/courses/{cid}/teachers/
    /api/courses/{cid}/teachers/{tid}/  （读|删）
    ```

* 课程下可添加教师

    ```
    /api/courses/{cid}/available-teachers/  （只读）
    ```
    
* 课程下学生

    ```
    /api/courses/{cid}/students/
    /api/courses/{cid}/students/{sid}/  （读|删）
    ```

* 课程下可添加学生

    ```
    /api/courses/{cid}/available-students/  （只读）
    ```

* 课程所在的课程组

    ```
    /api/courses/{cid}/groups/
    /api/courses/{cid}/groups/{gid}/    （读|删）
    ```

* 课程下的任务组

    ```
    /api/courses/{cid}/missions/
    /api/courses/{cid}/missions/{mid}/  （读|删）
    ```

#### 课程组

* 课程组

    ```
    /api/course-groups/
    /api/course-groups/{gid}/
    ```
    
* 课程组下教师

    ```
    /api/course-groups/{gid}/teachers/
    /api/course-groups/{gid}/teachers/{tid}/    （读|删）
    ```
    
* 课程组下可添加教师
    
    ```
    /api/course-groups/{gid}/available-teachers/  （只读）
    ```
    
* 课程组下课程

    ```
    /api/course-groups/{gid}/courses/
    /api/course-groups/{gid}/courses/{cid}/     （读|删）
    ```
    
* 课程组下可添加课程

    ```
    /api/course-groups/{gid}/available-courses/ （只读）
    ```

* 课程组下的任务组

    ```
    /api/course-groups/{gid}/missions/
    /api/course-groups/{gid}/missions/{mid}/  （读|删）
    ```

#### 任务组

* 任务组

    ```
    /api/mission-groups/
    /api/mission-groups/{gid}/
    ```

* 任务组下任务

    ```
    /api/mission-groups/{gid}/missions/
    /api/mission-groups/{gid}/missions/{mid}/   （读|删）
    ```

#### 任务

* 任务

    ```
    /api/missions/{mid}/
    ```
    
* 任务下的题目

    ```
    /api/missions/{mid}/problems/
    /api/missions/{mid}/problems/{pid}/ （读|删）
    ```

* 任务内的提交

    ```
    /api/missions/{mid}/submissions/
    /api/missions/{mid}/submissions/{sid}/ （读|更）
    ```

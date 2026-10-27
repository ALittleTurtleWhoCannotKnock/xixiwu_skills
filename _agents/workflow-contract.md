# 共享执行约定

供流程技能与 implementer 使用。tracker 的状态值域以目标仓库 `docs/agents/issue-tracker.md` 的声明为准；以下定义字段格式和默认语义。

## 基础模型

- 初始化由用户从当前工具实际可用的模型中选择，或明确选择 `inherit`，保存在目标仓库 `docs/agents/execution-mode.md` 的“基础模型”字段。模板不预填具体模型名或供应商。
- 分派方读取该字段，把用户选定的模型 ID 传给当前工具支持的模型参数；`inherit` 使用工具的原生继承方式。inline 模式使用主会话，无需单独切换模型。
- 项目尚未配置模型时沿用运行工具的默认规则；再次初始化时补齐选择引导，不自动指定模型。配置 ID 无法用于当前工具时，报告该字段和不兼容原因，不静默替换。
- Pi 构建使用 `--project-root` 指定项目，用户可用 `DEV_FLOW_MODEL` 单次覆盖；没有显式选择时不生成 `model` 字段。

## Tracker 产物与 Plan 引用

先读目标仓库 `docs/agents/issue-tracker.md`，每种产物只维护一个现行主存：

| 产物 | 本地 tracker | GitHub/GitLab tracker |
|------|--------------|----------------------|
| Spec | `.scratch/<feature>/spec.md` 或其版本文件 | Spec issue，版本定位沿用 tracker 约定 |
| Plan | `.scratch/<feature>/plan.md` | 独立 Plan issue，正文保存现行方案 |
| Ticket | `.scratch/<feature>/issues/<NN>-<slug>.md` | 每票一个独立 issue |

- 远程 Plan issue 标题可用 `[Plan] <Feature> 实施蓝图`，正文用 `Spec:` 引用当前执行版 Spec；Spec 正文用 `Plan:` 反向关联，Plan 正文列出关联 tickets。创建前先检查已有引用，已有 Plan issue 就更新同一 issue。
- ticket 分别记录 `Spec:` 和 `Plan:`；本地示例为 `Plan: plan.md#P2`，远程为 `Plan: #101 / P2`（跨仓库时使用完整 issue URL）。P2 是正文中的工作包编号，不依赖平台自动生成的 Markdown 锚点。
- 远程现行 plan 不放在 Spec 评论中，也不与本地文件双写。评论记录讨论、批准依据与变更原因；正文保存当前方案和 `**状态**: 待 review` / `**状态**: 已批准（日期）`。
- issue 的 open/closed 不代表 plan 的批准状态。读取批准戳记与对应授权证据，不因关闭 issue 而自动批准或解除执行限制。
- amend 仍维护同一个 Plan issue：更新正文和当前 `Spec:` 引用，不新建 plan-vN。Spec 的版本存放继续遵循 tracker 的既有约定，不用 Plan issue 编号推断 Spec 版本。
- 旧 plan 若仅在 Spec 评论中，继续维护时将当前有效内容迁到独立 Plan issue，保留原评论与批准证据，再更新本次涉及的引用；只读查询不执行迁移。

## 归属层级与列表展示

默认层级为 **Spec → Plan → Tickets**。已有明确的 Epic 时，在 Spec 上方关联该 Epic；不为补层级额外创建总单。`Parent:` 记录直接归属，`Spec:` 记录具体规格版本，`Plan:` 记录方案与 P<N>，`Blocked by:` 记录执行依赖，四者不互相代替。

| 产物 | `Parent:` |
|------|-----------|
| Spec | 用户或 tracker 已指定的 Epic 引用；没有时写 `none` |
| Plan | 当前 Spec 的文件/issue 引用 |
| Ticket | Plan 的文件/issue 引用，不带 P<N>；明确省略 Plan 时用 Spec，二者均省略时用已指定 Epic 或 `none (单票小改动)` |

旧产物缺少 `Parent:` 时，可从明确的 `Plan:` / `Spec:` 推导并标注“推导”；不能从编号、目录名或相似标题猜 Epic。写入本次涉及的产物时补齐归属，不批量改写历史票。版本续接是演进关系，旧 ticket 不是新 ticket 的归属父级。

### 本地文件

- 保留 `.scratch/<feature>/spec*.md`、同一 `plan.md` 和 `issues/<NN>-<slug>.md` 的平铺结构，不按层级搬动文件或为每个 P<N> 建目录。正文的 `Parent:` / `Spec:` / `Plan:` 路径统一相对 feature 目录。
- 首次保存 Spec 或 ticket 时创建/更新 `.scratch/<feature>/INDEX.md`；保存 Plan、拆票和 amend 时同步本次关联。INDEX 保留当前规格入口、同一 Plan 的链接、按归属缩进的 ticket 链接及规格演进记录。P<N> 可以作为分组标注，不是额外父文档。
- INDEX 中的 Markdown 链接相对 INDEX 所在目录，必须指向真实文件。尚未产生或明确省略的 Spec/Plan 写 `none (原因)`，不生成假文件或失效链接。历史规格与旧票保留并注明版本，不把所有挂在同一 Plan 下的票当作当前执行层。
- INDEX 是导航和当前版本入口，不复制方案正文、ticket Status 或 Plan 批准状态；状态从原文件读取。写入前重读当前版本及有关引用，存在冲突时报告，不覆盖其他人的更新。
- `.scratch/README.md` 维护 feature 到 `feature/INDEX.md` 的链接清单，保留其他说明。旧 feature 尚无 INDEX 时暂链接其目录；只读查询不代建索引。

INDEX 示例（仅列已经存在的产物）：

```markdown
# Feature: export
**当前版本**: [spec-v2.md](spec-v2.md)
Plan: [plan.md](plan.md)

## 层级
- [Spec v2](spec-v2.md)（当前）
  - [Plan](plan.md)
    - [04 JSON 导出](issues/04-json.md) — P2 / Spec v2
    - [01 CSV 导出](issues/01-csv.md) — P1 / Spec v1（历史）

## 演进
- [v1](spec.md)：CSV 导出
- [v2](spec-v2.md)：增加 JSON 格式
```

### GitHub

- 新建/更新本次产物时，按 `Parent:` 建立原生 parent/sub-issue 关系并读取核对；已是同一父级时复用，不重复创建 issue。正文引用仍保留，不能把 Markdown 互链称作已同步原生关系。
- 优先沿用项目的类型标签；未约定时使用 `spec` / `plan` / `ticket`，Epic 仅在已有该产物时标注。标题分别用 `[Spec]` / `[Plan]` / `[Ticket]` 前缀，便于仓库 Issues 列表区分。缺少标签时可创建本次所需标签；权限不足则保留标题分类并报告未同步项，不为标签重建 issue。
- 使用当前工具实际支持的层级接口。先分别检查 `gh issue create --help`、`gh issue edit --help` 和 `gh issue view --help`；旧版不支持相关参数时，用 `gh api` 或可用连接器访问 [Sub-issues API](https://docs.github.com/en/rest/issues/sub-issues)。API 的 `sub_issue_id` 是子 issue 的数值 **id**，不是列表中的 issue number；从实际查询结果取得。
- 添加前读取子 issue 的父级和目标父 issue 的子列表；确认对象可访问且没有冲突再写入。认证失败、403 或来源不明的 404 不能当作“没有父级”。已有其他父级时不强制替换，报告期望与实际；仅 `/amend` 中经核对的同一 feature 规格版本迁移适用下节规则。写入失败后读取实际结果，报告未同步关系及原因，不无限重试或重复建单。
- Projects 是可选展示入口。tracker 已配置或用户已指定目标 Project 时，把本次 issue 加入同一 Project；未指定时不创建 Project，不阻塞普通 Issues 流程。表格视图可打开 **View → Show hierarchy**，显示 Parent issue / Sub-issue progress；仓库 Issues 页保留分类与筛选入口，不承诺相同树形展示。参考 [GitHub 层级视图说明](https://github.blog/changelog/2026-03-19-hierarchy-view-in-github-projects-is-now-generally-available/)。
- GitLab 沿用上述逻辑字段和既有平台约定，原生层级能力按当前工具与权限探测，不直接套用 GitHub API。平台不支持时保留正文关系并明确说明展示限制。

### 规格演进与状态

- amend 继续维护同一个 Plan。新 Spec 继承已确认的 Epic；Plan 的 `Spec:` 与 `Parent:` 更新到当前规格，已有 ticket 的版本和状态保持原样，新票归属同一个 Plan。
- 远程规格仍在同一 issue 内演进时，Plan 的原生父级保持不变。版本另建 Spec issue 时，只有旧父级确为本次读取的上一 Spec、两版属于同一 feature 且本次变更已确认，才在写入前重读关系并将 Plan 移至新版 Spec；不重挂历史 tickets，不替换不明父级。发生并发变化或冲突时停止该关系写入并报告。
- 父子数量、子 issue 关闭比例、目录层级都不代表 Plan 已批准或业务已验收；不据此自动关闭父 issue、升级状态或解除依赖。`/find` 从原始状态源生成带版本与状态的树形快照，原生关系、正文字段或 INDEX 不一致时明确列出，不在查询时修复。

## Ticket 字段

每张 ticket 一个文件，最小格式：

```markdown
## Ticket 02: 评论数据模型与基础 API
Status: ready
Parent: plan.md
Spec: spec.md
Plan: plan.md#P2
Blocked by: 01-prefactor

**描述**: 创建和查询评论
**测试 seam**: HTTP API
**验证方式**: 在已有 API 测试文件中补充行为用例，复用 fixtures，先复现失败再实现
**测试用例**: 创建成功、查询列表、未登录返回 401
**验收标准**:
- 创建和查询接口符合约定
```

- `Parent:` 按上节记录直接归属；没有 Plan 时不强制补 Plan，也不把 blocker 写成父级。
- `Spec:` 指向所属 spec 版本；本地路径相对 feature 目录，远程 tracker 可用 issue 引用。
- `Plan:` 指向本地 plan 包或独立 Plan issue 中的包；与 spec 版本分别记录，不复用同一个来源字段。
- `Blocked by:` 使用 ticket 编号/文件名/issue 引用，无依赖写 `none`；外部条件也必须明确列出。
- 小改动允许 `Spec: none (原因)`、`Plan: none (单票小改动)`。省略的产品边界、技术决策、测试 seam 与验收标准必须在 ticket 中写清；不得要求执行者读取不存在的文档。
- `**验证方式**` 说明验证策略、已有测试落点或检查命令；旧票未填写时，按下节选择并记录。非运行行为的改动可将测试 seam 标为不适用并解释原因。
- 读取旧票时兼容 `**来源**: plan P<N>`、`**来源**: spec-vN`、`**依赖**:` 和 `**阻塞**:`。按内容区分来源；同类字段冲突时报告具体字段，不猜测、不忽略阻塞。新票使用上述标准字段，更新旧票时只规范本次触及的字段。

## 验证方式与测试组织

先检查项目已有测试框架、运行命令、相同测试边界的用例与 fixtures，再按改动语义选择验证方式，不只看文件后缀。Spec、plan、ticket 或用户已明确要求的检查必须保留，不能因失败、缺环境或希望少建文件而降级。

| 改动类型 | 默认验证方式 |
|----------|--------------|
| 新增/修改业务行为、接口契约、bug 修复 | 在约定 seam 复用或补充有意义的行为测试，先确认失败再实现；已有失败用例准确复现问题时直接复用 |
| 不改变外部行为的重构 | 修改前后运行已有相关回归测试；覆盖不足时先补充行为刻画，不为重构人为制造失败测试 |
| 纯文档、注释或措辞，不改变执行规则/契约 | 按内容检查链接、格式、渲染、示例命令或人工走查；不新增仅匹配文字/源码关键词的自证测试 |
| 配置、构建与依赖调整 | 执行适用的解析、类型检查、构建或受控冒烟验证；涉及运行逻辑或缺陷时补充相应行为回归 |
| 仅样式或布局 | 在要求的视口和状态下检查实际页面，可复用已有视觉回归；交互或业务变化仍按行为改动验证 |

技能指令、脚本示例或工作流文档改变执行语义时，需验证受影响的实际行为，例如隔离场景走查；不能因文件是 Markdown 就只检查文字。

**测试文件的组织：**

- 优先扩展现有测试文件与 fixtures；同一功能/测试边界的多组输入使用现有框架的参数化、表驱动或子测试，不按 ticket、函数或每项断言各建一个文件。
- 新文件只在独立功能/边界确实没有合适落点，或项目已有拆分约定时创建，报告新增理由；不硬设文件数量，也不把所有测试强塞进一个大文件。
- 已有覆盖实际验证了本次验收时，直接复用，不再复制一份；同一行为不默认在单测、Service、API 和 E2E 各写一套，额外层级应覆盖独立风险。
- 断言用户可观察的行为和契约；不以逐行复刻实现、只检查源码存在某字符串来代替行为验证。不为减少文件而削弱断言或省略关键场景。

**持久回归与临时验证：**

- 有长期回归价值的行为测试留在项目测试体系中，bug 修复保留能防止复发的覆盖。一次性探针、诊断脚本和试验用测试放系统临时目录，结果写入 ticket/报告。
- 只清理本次产生的临时产物；不因文件多而批量删除既有测试。若把本次临时用例迁入现有测试，先确认等效覆盖再清理临时副本。
- 报告所选验证方式、复用/新增的测试位置、实际运行命令与结果、不适用项及原因。必要检查失败或未运行仍阻塞完成，不能换成更弱的检查后报通过。

## 状态与依赖

新初始化的 tracker 声明 `ready / claimed / code-complete / resolved / parked`：

| 状态 | 语义 | 解除 ticket 依赖 |
|------|------|-----------------|
| ready | 待执行 | 否 |
| claimed | 执行中，或必要自动检查失败/未运行 | 否 |
| code-complete | 代码实现与必要自动检查通过，仍待人工/真机验收或收尾 checkpoint | 是，提示尚未最终验收 |
| resolved | 所有必需验收通过，收尾 checkpoint 已处理 | 是 |
| parked | 搁置，等待外部条件或决策 | 否 |

- 主会话负责领取和更新状态；执行者报告证据。不得把失败或未运行的必要自动检查当作通过，不得用 `resolved` 掩盖未完成的人工/真机验收。
- 每票验证后就更新状态和依赖。提交节奏不决定依赖解除：squash 下可继续执行依赖 `code-complete` 的下一票；明确声明的外部验证条件仍需单独满足。
- Git 提交与验收状态分开记录。只有用户明确授权才提交/推送；用户选择暂不提交不等于测试失败，未提交也不自动等于最终验收完成。
- 旧 tracker 保持其已声明的值域和完成语义。使用 `code-complete` 前需补齐 tracker 对该状态及依赖语义的声明；不能写入未声明状态，也不能为绕过缺失约定提前标记 `resolved`。

## 改动规模与输入

- 常规 feature：spec 定义产品边界，已批准的 plan 定义技术路径，ticket 定义执行与验收。
- 单票小改动：允许省略 spec/plan，必要决策收在已确认的 ticket 中；无 plan 时跳过 plan 锚点检查，仍运行约定的测试与验收。
- 无 ticket 的微小改动：遵循用户明确需求和仓库验证方式，在已有文档或 changelog 留记录；不强制补齐整套流程。

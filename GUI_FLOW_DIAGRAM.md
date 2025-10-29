# LLM Manager - GUI Flow Diagram

## Complete Application Flow

```mermaid
graph TD
    Start([Application Launch]) --> MainWindow[Main Window<br/>LLMManagerApp]

    %% Main Window Structure
    MainWindow --> Header[Header Bar]
    MainWindow --> RootPane[Root Pane<br/>Key: 6]
    MainWindow --> Footer[Footer Bar<br/>Key Bindings Display]

    %% Root Pane Children
    RootPane --> Row1[Row 1: Horizontal]
    RootPane --> Row2[Row 2: Horizontal]
    RootPane --> Row3[Row 3: Vertical]

    Row1 --> UserPane[User Prompt<br/>Key: 1]
    Row1 --> SystemPane[System Prompt<br/>Key: 2]
    Row2 --> ContextPane[Context<br/>Key: 3]
    Row2 --> LLMPane[LLM Selection<br/>Key: 4]
    Row3 --> ResponsePane[Response<br/>Key: 5]

    %% Navigation Methods
    MainWindow -->|Tab| CycleNext[Focus Next Pane]
    MainWindow -->|Shift+Tab| CyclePrev[Focus Previous Pane]
    MainWindow -->|1-6| DirectNav[Direct Pane Focus]

    CycleNext --> MainWindow
    CyclePrev --> MainWindow
    DirectNav --> MainWindow

    %% Modal Screens
    MainWindow -->|? key| HelpScreen[Help Screen]
    HelpScreen -->|ESC/q/?| MainWindow

    MainWindow -->|ESC key| PaneMenu[Pane Menu Screen]
    PaneMenu -->|ESC/q| MainWindow
    PaneMenu --> MenuActions[Menu Actions]

    %% Pane Menu Actions
    MenuActions -->|Select Pane| FocusAction[Focus/Unhide Pane]
    MenuActions -->|Hide Pane| HideAction[Hide Selected Pane]
    MenuActions -->|Unhide Pane| UnhideAction[Unhide Selected Pane]
    MenuActions -->|Hide All| HideAllAction[Hide All Children]
    MenuActions -->|Show All| ShowAllAction[Show All Children]
    MenuActions -->|Reset Layout| ResetAction[Reset to Default Layout]

    FocusAction --> MainWindow
    HideAction --> PaneMenu
    UnhideAction --> PaneMenu
    HideAllAction --> MainWindow
    ShowAllAction --> MainWindow
    ResetAction --> MainWindow

    %% Prompt Manager Flow
    UserPane -->|p key| PromptMgrUser[Prompt Manager<br/>User Prompt]
    SystemPane -->|p key| PromptMgrSystem[Prompt Manager<br/>System Prompt]
    ContextPane -->|p key| PromptMgrContext[Prompt Manager<br/>Context]

    PromptMgrUser --> PromptMenu[Prompt Menu]
    PromptMgrSystem --> PromptMenu
    PromptMgrContext --> PromptMenu

    PromptMenu -->|List| ListPrompts[Show Prompt Files]
    PromptMenu -->|Load| LoadPrompts[Select File to Load]
    PromptMenu -->|Save| SavePrompts[Enter Filename]
    PromptMenu -->|Cancel| MainWindow

    ListPrompts -->|Select| LoadMode[Choose Load Mode]
    LoadPrompts -->|Select| LoadMode

    LoadMode -->|R: Replace| ReplaceContent[Replace Pane Content]
    LoadMode -->|A: Append| AppendContent[Append to Pane Content]
    LoadMode -->|I: Insert| InsertContent[Insert at Cursor]
    LoadMode -->|Back| LoadPrompts

    ReplaceContent --> MainWindow
    AppendContent --> MainWindow
    InsertContent --> MainWindow

    SavePrompts -->|Save| SaveFile[Write to Prompts Dir]
    SavePrompts -->|Cancel| MainWindow
    SaveFile --> MainWindow

    %% External Editor Flow
    UserPane -->|e key| NvimUser[nvim: User Prompt]
    SystemPane -->|e key| NvimSystem[nvim: System Prompt]
    ContextPane -->|e key| NvimContext[nvim: Context]

    NvimUser -->|Save & Exit| MainWindow
    NvimSystem -->|Save & Exit| MainWindow
    NvimContext -->|Save & Exit| MainWindow

    %% Edit Mode Flow
    UserPane -->|i key| EditModeUser[Edit Mode: User]
    SystemPane -->|i key| EditModeSystem[Edit Mode: System]
    ContextPane -->|i key| EditModeContext[Edit Mode: Context]

    EditModeUser -->|ESC| UserPane
    EditModeSystem -->|ESC| SystemPane
    EditModeContext -->|ESC| ContextPane

    EditModeUser -->|Type text| EditModeUser
    EditModeSystem -->|Type text| EditModeSystem
    EditModeContext -->|Type text| EditModeContext

    %% LLM Operations
    MainWindow -->|Ctrl+J| SendLLM[Send to LLM]
    SendLLM --> ValidateModel{Model Selected?}
    ValidateModel -->|No| ErrorNoModel[Notify: Select Model]
    ValidateModel -->|Yes| ValidatePrompt{User Prompt?}

    ErrorNoModel --> MainWindow

    ValidatePrompt -->|Empty| ErrorNoPrompt[Notify: Empty Prompt]
    ValidatePrompt -->|Has Text| CheckStreaming{Streaming Enabled?}

    ErrorNoPrompt --> MainWindow

    CheckStreaming -->|Yes| StreamResponse[Stream Response<br/>Show chunks in real-time]
    CheckStreaming -->|No| WaitResponse[Wait for Response<br/>Show when complete]

    StreamResponse --> UpdateResponse[Update Response Pane]
    WaitResponse --> UpdateResponse
    UpdateResponse --> SaveHistory[Save to Conversation History]
    SaveHistory --> MainWindow

    %% Response Pane Actions
    ResponsePane -->|s key| ToggleStream[Toggle Streaming Mode]
    ResponsePane -->|c key| ClearResponse[Clear Response Content]

    ToggleStream --> MainWindow
    ClearResponse --> MainWindow

    %% LLM Selection Actions
    LLMPane -->|↑/↓ keys| NavModels[Navigate Model List]
    LLMPane -->|Enter| SelectModel[Select LLM Model]

    NavModels --> LLMPane
    SelectModel --> InitModel[Initialize Model/API]
    InitModel --> MainWindow

    %% Save Operations
    MainWindow -->|Ctrl+S| SaveFocused{Which Pane Focused?}
    SaveFocused -->|User| SaveUser[Save User Prompt]
    SaveFocused -->|System| SaveSystem[Save System Prompt]
    SaveFocused -->|Context| SaveContext[Save Context]
    SaveFocused -->|Other| ErrorNoSave[Notify: No Editable Pane]

    SaveUser --> MainWindow
    SaveSystem --> MainWindow
    SaveContext --> MainWindow
    ErrorNoSave --> MainWindow

    %% Layout Management
    MainWindow -->|m key| ToggleMax[Toggle Maximize Focused Pane]
    MainWindow -->|n key| ToggleMin[Toggle Minimize Focused Pane]
    MainWindow -->|Ctrl+↑| IncHeight[Increase Pane Height]
    MainWindow -->|Ctrl+↓| DecHeight[Decrease Pane Height]

    ToggleMax --> MainWindow
    ToggleMin --> MainWindow
    IncHeight --> MainWindow
    DecHeight --> MainWindow

    %% Conversation Management
    MainWindow -->|Ctrl+E| ExportConv[Export Conversation]
    MainWindow -->|Ctrl+I| ImportConv[Import Conversation<br/>Not Implemented]

    ExportConv --> SaveJSON[Save JSON to ~/]
    SaveJSON --> MainWindow
    ImportConv --> ErrorNotImpl[Notify: Not Implemented]
    ErrorNotImpl --> MainWindow

    %% Exit
    MainWindow -->|q key| ConfirmQuit{Confirm Exit?}
    ConfirmQuit -->|Yes| Exit([Application Exit])
    ConfirmQuit -->|No| MainWindow

    %% Styling
    classDef mainStyle fill:#2196F3,stroke:#1565C0,color:#fff
    classDef paneStyle fill:#4CAF50,stroke:#2E7D32,color:#fff
    classDef modalStyle fill:#FF9800,stroke:#E65100,color:#fff
    classDef actionStyle fill:#9C27B0,stroke:#6A1B9A,color:#fff
    classDef flowStyle fill:#607D8B,stroke:#37474F,color:#fff
    classDef errorStyle fill:#F44336,stroke:#C62828,color:#fff

    class MainWindow,RootPane mainStyle
    class UserPane,SystemPane,ContextPane,LLMPane,ResponsePane paneStyle
    class HelpScreen,PaneMenu,PromptMenu,PromptMgrUser,PromptMgrSystem,PromptMgrContext modalStyle
    class SendLLM,SaveFocused,ToggleMax,ToggleMin,ExportConv actionStyle
    class ValidateModel,ValidatePrompt,CheckStreaming,ConfirmQuit flowStyle
    class ErrorNoModel,ErrorNoPrompt,ErrorNoSave,ErrorNotImpl errorStyle
```

## Screen Hierarchy

```mermaid
graph TD
    App[LLMManagerApp<br/>Main Application]

    %% Persistent Screens
    App --> Main[Main Screen<br/>Always Visible]

    Main --> Header[Header Widget]
    Main --> Content[Content Area<br/>Root Pane + Children]
    Main --> Footer[Footer Widget]

    %% Modal Screens - Overlay Main
    App -->|Modal| Help[Help Screen<br/>ModalScreen]
    App -->|Modal| Menu[Pane Menu<br/>ModalScreen]
    App -->|Modal| PromptMgr[Prompt Manager<br/>ModalScreen]

    %% External Process
    App -->|Suspend| Nvim[External nvim Process]

    %% Modal Screen Details
    Help --> HelpContent[Keybinding Reference<br/>Scrollable]

    Menu --> MenuHierarchy[Pane Hierarchy Display]
    Menu --> MenuActions[Action Options]

    PromptMgr --> PromptList[File List View]
    PromptMgr --> PromptLoad[Load Mode Selection]
    PromptMgr --> PromptSave[Save Input Form]

    classDef persistent fill:#2196F3,stroke:#1565C0,color:#fff
    classDef modal fill:#FF9800,stroke:#E65100,color:#fff
    classDef external fill:#F44336,stroke:#C62828,color:#fff

    class App,Main,Header,Content,Footer persistent
    class Help,Menu,PromptMgr,HelpContent,MenuHierarchy,MenuActions,PromptList,PromptLoad,PromptSave modal
    class Nvim external
```

## Pane State Transitions

```mermaid
stateDiagram-v2
    [*] --> Normal: Pane Created

    Normal --> Minimized: Press 'n'<br/>or Ctrl+↓ from 1fr
    Normal --> Maximized: Press 'm'<br/>or Ctrl+↑ from 3fr
    Normal --> Height2fr: Press Ctrl+↑
    Normal --> Height3fr: Press Ctrl+↑ twice

    Height2fr --> Normal: Press Ctrl+↓
    Height2fr --> Height3fr: Press Ctrl+↑

    Height3fr --> Height2fr: Press Ctrl+↓
    Height3fr --> Maximized: Press Ctrl+↑

    Minimized --> Normal: Press 'n'<br/>or Ctrl+↑
    Minimized --> Maximized: Press Ctrl+↓<br/>(wraps around)

    Maximized --> Normal: Press 'm'
    Maximized --> Height3fr: Press Ctrl+↓
    Maximized --> Minimized: Press Ctrl+↑<br/>(wraps around)

    note right of Normal
        Height: 1fr (equal)
        All content visible
    end note

    note right of Height2fr
        Height: 2fr (double)
        More space for content
    end note

    note right of Height3fr
        Height: 3fr (triple)
        Maximum normal height
    end note

    note right of Minimized
        Height: 3 lines
        Content hidden
        Title visible only
    end note

    note right of Maximized
        Full screen
        Other panes hidden
    end note
```

## Edit Mode State Machine (EditablePane)

```mermaid
stateDiagram-v2
    [*] --> CommandMode: Pane Mounted

    CommandMode --> EditMode: Press 'i'
    EditMode --> CommandMode: Press ESC

    state CommandMode {
        [*] --> PaneHasFocus
        PaneHasFocus --> ListeningForCommands

        note right of ListeningForCommands
            Active Keys:
            - 1-6: Navigate panes
            - e: Open nvim
            - p: Prompt manager
            - Ctrl+S: Save
            - m/n: Maximize/Minimize
            - Tab: Next pane
        end note
    }

    state EditMode {
        [*] --> TextAreaHasFocus
        TextAreaHasFocus --> TypingText

        note right of TypingText
            Active Keys:
            - All text input
            - Arrow keys
            - Ctrl+A/C/V/Z/Y
            - Most app keys disabled
        end note
    }

    CommandMode --> [*]: Pane Unmounted
    EditMode --> [*]: Pane Unmounted
```

## Prompt Manager Workflow

```mermaid
graph TD
    Start([Press 'p' on Editable Pane]) --> CheckPane{Editable Pane?}

    CheckPane -->|No| Error[Show Error:<br/>Only works on User/System/Context]
    CheckPane -->|Yes| OpenManager[Open Prompt Manager]

    Error --> End([Return to Main Window])

    OpenManager --> ShowMenu[Show Main Menu]
    ShowMenu --> MenuChoice{User Selection}

    MenuChoice -->|List| ShowList[Display All .txt Files<br/>in prompts/ directory]
    MenuChoice -->|Load| ShowLoadList[Display .txt Files<br/>for Loading]
    MenuChoice -->|Save| ShowSaveForm[Show Filename Input]
    MenuChoice -->|Cancel| End

    ShowList --> ListChoice{User Action}
    ListChoice -->|Select File| LoadModeSelect
    ListChoice -->|Back| ShowMenu

    ShowLoadList --> LoadChoice{User Action}
    LoadChoice -->|Select File| LoadModeSelect[Select Load Mode]
    LoadChoice -->|Back| ShowMenu

    LoadModeSelect --> ModeChoice{Load Mode?}
    ModeChoice -->|R: Replace| ReadFile1[Read File Content]
    ModeChoice -->|A: Append| ReadFile2[Read File Content]
    ModeChoice -->|I: Insert| ReadFile3[Read File Content]
    ModeChoice -->|Back| ShowLoadList

    ReadFile1 --> Replace[Replace Entire Pane Content]
    ReadFile2 --> Append[Append to End of Content]
    ReadFile3 --> GetCursor[Get Cursor Position]

    GetCursor --> Insert[Insert at Cursor Position]

    Replace --> Notify1[Notify: Loaded - replaced]
    Append --> Notify2[Notify: Loaded - appended]
    Insert --> Notify3[Notify: Loaded - inserted]

    Notify1 --> End
    Notify2 --> End
    Notify3 --> End

    ShowSaveForm --> InputName[User Enters Filename]
    InputName --> ValidateName{Valid Name?}

    ValidateName -->|Empty| ShowSaveForm
    ValidateName -->|Valid| AddExtension[Add .txt if missing]

    AddExtension --> WriteFile[Write Content to<br/>prompts/filename.txt]
    WriteFile --> NotifySave[Notify: Saved]
    NotifySave --> End

    classDef startEnd fill:#4CAF50,stroke:#2E7D32,color:#fff
    classDef screen fill:#2196F3,stroke:#1565C0,color:#fff
    classDef action fill:#FF9800,stroke:#E65100,color:#fff
    classDef decision fill:#9C27B0,stroke:#6A1B9A,color:#fff

    class Start,End startEnd
    class OpenManager,ShowMenu,ShowList,ShowLoadList,ShowSaveForm,LoadModeSelect screen
    class ReadFile1,ReadFile2,ReadFile3,Replace,Append,Insert,GetCursor,WriteFile,AddExtension action
    class CheckPane,MenuChoice,ListChoice,LoadChoice,ModeChoice,ValidateName decision
```

## LLM Send Workflow

```mermaid
graph TD
    Start([Press Ctrl+J]) --> GetModel[Get Selected Model<br/>from LLM Pane]

    GetModel --> CheckModel{Model<br/>Selected?}
    CheckModel -->|No| ErrorModel[Notify: Please select model<br/>Press 4 to focus LLM pane]
    CheckModel -->|Yes| CheckCurrent{Current Model<br/>Matches?}

    ErrorModel --> End([Return to Main Window])

    CheckCurrent -->|No| InitModel[Initialize Model<br/>Set API Client]
    CheckCurrent -->|Yes| GetPrompts[Get Content from Panes]

    InitModel --> InitSuccess{Init Success?}
    InitSuccess -->|No| ErrorInit[Notify: Check API keys]
    InitSuccess -->|Yes| GetPrompts

    ErrorInit --> End

    GetPrompts --> Content[User Prompt<br/>System Prompt<br/>Context]
    Content --> ValidateUser{User Prompt<br/>Not Empty?}

    ValidateUser -->|Empty| ErrorEmpty[Notify: User prompt is empty]
    ValidateUser -->|Not Empty| ClearResponse[Clear Response Pane]

    ErrorEmpty --> End

    ClearResponse --> CheckStreaming{Streaming<br/>Enabled?}

    CheckStreaming -->|Yes| StreamWorker[Start Streaming Worker<br/>Async Task]
    CheckStreaming -->|No| NonStreamWorker[Start Non-Streaming Worker<br/>Async Task]

    StreamWorker --> StreamAPI[Call LLM API<br/>Stream Mode]
    StreamAPI --> StreamLoop[For Each Chunk]

    StreamLoop --> AppendChunk[Append to Response Pane]
    AppendChunk --> MoreChunks{More Chunks?}

    MoreChunks -->|Yes| StreamLoop
    MoreChunks -->|No| Complete[Set Status: Complete]

    NonStreamWorker --> NonStreamAPI[Call LLM API<br/>Wait for Full Response]
    NonStreamAPI --> SetResponse[Set Response Pane Content]
    SetResponse --> Complete

    Complete --> SaveHistory[Save to Conversation History<br/>JSON Format]
    SaveHistory --> NotifySuccess[Notify: Response received]

    NotifySuccess --> End

    StreamAPI -->|Error| HandleError[Show Error in Response]
    NonStreamAPI -->|Error| HandleError
    HandleError --> NotifyError[Notify: Error message]
    NotifyError --> End

    classDef startEnd fill:#4CAF50,stroke:#2E7D32,color:#fff
    classDef action fill:#2196F3,stroke:#1565C0,color:#fff
    classDef decision fill:#9C27B0,stroke:#6A1B9A,color:#fff
    classDef error fill:#F44336,stroke:#C62828,color:#fff
    classDef success fill:#8BC34A,stroke:#558B2F,color:#fff

    class Start,End startEnd
    class GetModel,InitModel,GetPrompts,Content,ClearResponse,StreamWorker,NonStreamWorker,StreamAPI,NonStreamAPI,AppendChunk,SetResponse,Complete,SaveHistory action
    class CheckModel,CheckCurrent,InitSuccess,ValidateUser,CheckStreaming,MoreChunks decision
    class ErrorModel,ErrorInit,ErrorEmpty,HandleError,NotifyError error
    class NotifySuccess success
```

## Key to Diagram Elements

### Node Shapes
- **Rectangle**: Screen/View
- **Rounded Rectangle**: Process/Action
- **Diamond**: Decision Point
- **Circle**: Start/End Point

### Color Coding
- **Blue** (#2196F3): Main screens/primary elements
- **Green** (#4CAF50): Panes/content areas
- **Orange** (#FF9800): Modal screens/overlays
- **Purple** (#9C27B0): Actions/operations
- **Gray** (#607D8B): Flow control/decisions
- **Red** (#F44336): Errors/external processes

### Connection Types
- **Solid Arrow**: User action/navigation
- **Dashed Arrow**: Automatic transition
- **Bold Arrow**: Primary flow path

## Usage Notes

1. **Main Flow Diagram**: Shows complete application navigation including all screens and actions
2. **Screen Hierarchy**: Shows structural relationship between persistent and modal screens
3. **State Diagrams**: Shows pane state transitions and edit mode behavior
4. **Workflow Diagrams**: Shows detailed flows for complex operations (Prompt Manager, LLM Send)

These diagrams can be viewed in any Markdown renderer that supports Mermaid (GitHub, GitLab, VS Code with extension, etc.)

# Merged Harness Workflow Diagram

```mermaid
flowchart TD
    subgraph SIGNAL["SIGNAL LAYER"]
        M[MacroSignalScout<br/>weekly LLM-driven]
        I[IndiaNewsScout<br/>daily LLM-driven]
        X[XScoutSenseAgent<br/>browser: X home feed]
        R[RedditScoutSenseAgent<br/>browser: subreddits]
    end

    M --> DIGEST[signals/<date>-macro-digest.md]
    I --> DIGEST2[signals/<date>-india-news-digest.md]
    X --> CLUSTER1[x_run/<date>_x_clusters.md]
    R --> CLUSTER2[reddit_run/<date>_reddit_clusters.md]

    DIGEST --> SELECT
    DIGEST2 --> SELECT
    CLUSTER1 -.future.-> SELECT
    CLUSTER2 -.future.-> SELECT

    subgraph GATE1["HUMAN GATE"]
        SELECT[Operator selects<br/>signal + surfaces]
    end

    SELECT --> TICKET[state/tickets/<date>-<id>.md]

    TICKET --> RESEARCH[Layer2ResearchAgentFull]
    RESEARCH --> RESEARCH_OUT[drafts/<ticket>/research.md]

    RESEARCH_OUT --> WRITE[Layer2Writer]
    WRITE --> BLOG[blog.md]
    WRITE --> THREAD[thread.md]
    WRITE --> CAR_LI[carousel_linkedin.md]
    WRITE --> CAR_IG[carousel_instagram.md]
    WRITE --> INFO[infographic.md]

    BLOG --> REVIEW
    THREAD --> REVIEW
    CAR_LI --> REVIEW
    CAR_IG --> REVIEW
    INFO --> REVIEW

    REVIEW[Layer2MarketsReviewerFull] --> REVIEW_OUT[reviews/<ticket>/markets-review.md]

    REVIEW_OUT --> CORRECT{correction loop}
    CORRECT -->|loop ≤ 2| WRITE
    CORRECT -->|done| SEO

    SEO[Layer2SEOAuditor] --> SEO_OUT[blog.md final corrections]

    SEO_OUT --> APPROVE[HUMAN GATE<br/>publish approval]

    APPROVE --> PUBLISH[Layer2PublisherFull]
    PUBLISH --> FINAL[final/]

    FINAL -.-> POSTIZ[Postiz VPS<br/>post to surfaces]
    POSTIZ -.-> RECEIPT[receipt with postiz_post_id]

    RECEIPT -.-> WAIT[WAIT 14 days]
    WAIT -.-> ANALYTICS[AnalyticsAgent<br/>fetch Postiz metrics]
    ANALYTICS -.-> REPORT[analytics/reports/<date>.md]
    REPORT -.-> HUMAN_REVIEW[Human reviews patterns]
    HUMAN_REVIEW -.-> LESSONS[Write lessons to AgentMemory]
    LESSONS -.-> M
    LESSONS -.-> I
    LESSONS -.-> RESEARCH
    LESSONS -.-> WRITE

    style SIGNAL fill:#e1f5fe
    style GATE1 fill:#fff3e0
    style APPROVE fill:#fff3e0
    style POSTIZ fill:#f3e5f5
    style ANALYTICS fill:#f3e5f5
    style LESSONS fill:#e8f5e9
```

## Legend

- **Blue boxes**: Signal scouts
- **Orange boxes**: Human gates
- **Purple boxes**: Future Postiz + analytics layer
- **Green box**: Learning / memory
- **Dotted lines**: Future integrations not built yet

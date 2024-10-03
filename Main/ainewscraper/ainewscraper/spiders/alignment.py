import scrapy
import os, json
import datetime
from ainewscraper.items import AinewscraperItem

class AlignmentSpider(scrapy.Spider):
    name = "alignment"
    allowed_domains = ["alignmentforum.org"]
    
    def start_requests(self):
        now = datetime.datetime.now()
        year = now.year
        month = now.month
        day = now.day
        
        url = "https://www.alignmentforum.org/graphql"
        
        query = """
        query multiPostQuery($input: MultiPostInput) {
          posts(input: $input) {
            results {
              ...PostsListWithVotes
              __typename
            }
            totalCount
            __typename
          }
        }
        
        fragment PostsListWithVotes on Post {
          ...PostsList
          currentUserVote
          currentUserExtendedVote
          podcastEpisode {
            _id
            title
            podcast {
              _id
              title
              applePodcastLink
              spotifyPodcastLink
              __typename
            }
            episodeLink
            externalEpisodeId
            __typename
          }
          __typename
        }
        
        fragment PostsList on Post {
          ...PostsListBase
          deletedDraft
          contents {
            _id
            htmlHighlight
            plaintextDescription
            wordCount
            version
            __typename
          }
          fmCrosspost
          __typename
        }
        
        fragment PostsListBase on Post {
          ...PostsBase
          ...PostsAuthors
          readTimeMinutes
          rejectedReason
          customHighlight {
            _id
            html
            plaintextDescription
            __typename
          }
          lastPromotedComment {
            _id
            user {
              ...UsersMinimumInfo
              __typename
            }
            __typename
          }
          bestAnswer {
            ...CommentsList
            __typename
          }
          tags {
            ...TagPreviewFragment
            __typename
          }
          socialPreviewData {
            _id
            imageUrl
            __typename
          }
          feedId
          totalDialogueResponseCount
          unreadDebateResponseCount
          dialogTooltipPreview
          disableSidenotes
          __typename
        }
        
        fragment PostsBase on Post {
          ...PostsMinimumInfo
          url
          postedAt
          createdAt
          sticky
          metaSticky
          stickyPriority
          status
          frontpageDate
          meta
          deletedDraft
          postCategory
          tagRelevance
          shareWithUsers
          sharingSettings
          linkSharingKey
          contents_latest
          commentCount
          voteCount
          baseScore
          extendedScore
          emojiReactors
          unlisted
          score
          lastVisitedAt
          isFuture
          isRead
          lastCommentedAt
          lastCommentPromotedAt
          canonicalCollectionSlug
          curatedDate
          commentsLocked
          commentsLockedToAccountsCreatedAfter
          debate
          question
          hiddenRelatedQuestion
          originalPostRelationSourceId
          userId
          location
          googleLocation
          onlineEvent
          globalEvent
          startTime
          endTime
          localStartTime
          localEndTime
          eventRegistrationLink
          joinEventLink
          facebookLink
          meetupLink
          website
          contactInfo
          isEvent
          eventImageId
          eventType
          types
          groupId
          reviewedByUserId
          suggestForCuratedUserIds
          suggestForCuratedUsernames
          reviewForCuratedUserId
          authorIsUnreviewed
          afDate
          suggestForAlignmentUserIds
          reviewForAlignmentUserId
          afBaseScore
          afExtendedScore
          afCommentCount
          afLastCommentedAt
          afSticky
          hideAuthor
          moderationStyle
          ignoreRateLimits
          submitToFrontpage
          shortform
          onlyVisibleToLoggedIn
          onlyVisibleToEstablishedAccounts
          reviewCount
          reviewVoteCount
          positiveReviewVoteCount
          manifoldReviewMarketId
          annualReviewMarketProbability
          annualReviewMarketIsResolved
          annualReviewMarketYear
          annualReviewMarketUrl
          group {
            _id
            name
            organizerIds
            __typename
          }
          podcastEpisodeId
          forceAllowType3Audio
          nominationCount2019
          reviewCount2019
          votingSystem
          disableRecommendation
          __typename
        }
        
        fragment PostsMinimumInfo on Post {
          _id
          slug
          title
          draft
          shortform
          hideCommentKarma
          af
          currentUserReviewVote {
            _id
            qualitativeScore
            quadraticScore
            __typename
          }
          userId
          coauthorStatuses
          hasCoauthorPermission
          rejected
          debate
          collabEditorDialogue
          __typename
        }
        
        fragment PostsAuthors on Post {
          user {
            ...UsersMinimumInfo
            biography {
              ...RevisionDisplay
              __typename
            }
            profileImageId
            moderationStyle
            bannedUserIds
            moderatorAssistance
            __typename
          }
          coauthors {
            ...UsersMinimumInfo
            __typename
          }
          __typename
        }
        
        fragment UsersMinimumInfo on User {
          _id
          slug
          createdAt
          username
          displayName
          profileImageId
          previousDisplayName
          fullName
          karma
          afKarma
          deleted
          isAdmin
          htmlBio
          jobTitle
          organization
          postCount
          commentCount
          sequenceCount
          afPostCount
          afCommentCount
          spamRiskScore
          tagRevisionCount
          reviewedByUserId
          __typename
        }
        
        fragment RevisionDisplay on Revision {
          _id
          version
          updateType
          editedAt
          userId
          html
          commitMessage
          wordCount
          htmlHighlight
          plaintextDescription
          __typename
        }
        
        fragment CommentsList on Comment {
          _id
          postId
          tagId
          tag {
            slug
            __typename
          }
          relevantTagIds
          relevantTags {
            ...TagPreviewFragment
            __typename
          }
          tagCommentType
          parentCommentId
          topLevelCommentId
          descendentCount
          title
          contents {
            _id
            html
            plaintextMainText
            wordCount
            __typename
          }
          postedAt
          repliesBlockedUntil
          userId
          deleted
          deletedPublic
          deletedByUserId
          deletedReason
          hideAuthor
          authorIsUnreviewed
          user {
            ...UsersMinimumInfo
            __typename
          }
          currentUserVote
          currentUserExtendedVote
          baseScore
          extendedScore
          score
          voteCount
          emojiReactors
          af
          afDate
          moveToAlignmentUserId
          afBaseScore
          afExtendedScore
          suggestForAlignmentUserIds
          reviewForAlignmentUserId
          needsReview
          answer
          parentAnswerId
          retracted
          postVersion
          reviewedByUserId
          shortform
          shortformFrontpage
          lastSubthreadActivity
          moderatorHat
          hideModeratorHat
          nominatedForReview
          reviewingForReview
          promoted
          promotedByUser {
            ...UsersMinimumInfo
            __typename
          }
          directChildrenCount
          votingSystem
          isPinnedOnProfile
          debateResponse
          rejected
          rejectedReason
          modGPTRecommendation
          originalDialogueId
          __typename
        }
        
        fragment TagPreviewFragment on Tag {
          ...TagBasicInfo
          parentTag {
            ...TagBasicInfo
            __typename
          }
          subTags {
            ...TagBasicInfo
            __typename
          }
          description {
            _id
            htmlHighlight
            __typename
          }
          canVoteOnRels
          __typename
        }
        
        fragment TagBasicInfo on Tag {
          _id
          userId
          name
          shortName
          slug
          core
          postCount
          adminOnly
          canEditUserIds
          suggestedAsFilter
          needsReview
          descriptionTruncationCount
          createdAt
          wikiOnly
          deleted
          isSubforum
          noindex
          __typename
        }
        """
        
        variables = {
            "input": {
                "terms": {
                    "karmaThreshold": -10,
                    "excludeEvents": True,
                    "hideCommunity": False,
                    "filter": "all",
                    "sortedBy": "magic",
                    "after": f"{year}-{month-1:02d}-01",
                    "before": f"{year}-{month:02d}-{day:02d}",
                    "limit": 50
                },
                "enableCache": False,
                "enableTotal": False
            }
        }
        
        yield scrapy.Request(
            url,
            method='POST',
            body=json.dumps({
                'operationName': 'multiPostQuery',
                'query': query,
                'variables': variables
            }),
            headers={'Content-Type': 'application/json'},
            callback=self.parse
        )

    def parse(self, response):
        data = json.loads(response.text)
        posts = data['data']['posts']['results']
        
        for post in posts:
            item = AinewscraperItem()
            
            item["url"] = f"https://www.alignmentforum.org/posts/{post['_id']}/{post['slug']}"
            item["title"] = post['title']
            item["author"] = post['user']['displayName']
            item["date"] = post['postedAt']

            # Make a new request to fetch the content, passing the item as meta
            yield scrapy.Request(item["url"], callback=self.parse_content, meta={'item': item})

    def parse_content(self, response):
        item = response.meta['item']
        item["content"] = ' '.join(response.css('#postContent .InlineReactSelectionWrapper-root ::text').getall()).strip()
        
        self.write_json(item)
        yield item

    def write_json(self, item):
        if not os.path.exists('output'):
            os.makedirs('output')
        
        filename = f"output/{item['url'].split('/')[-1]}.json"
        with open(filename, 'w') as f:
            json.dump(dict(item), f, indent=4)
        self.logger.info(f"Saved item to {filename}")
        